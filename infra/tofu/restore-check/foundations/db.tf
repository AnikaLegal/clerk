# The monthly database restore check, run entirely inside AWS (TEC-2065):
# an EventBridge schedule invokes the restore-check-db Lambda durable
# function, which runs the check as a Fargate task and reports to Slack.
# See docs/restore-check.md and infra/restore-check/db-lambda.py.
#
# Deliberately NOT defined here: the three SecureString parameters the
# check depends on. Create them by hand so no secret ever enters state
# (the Sentry URL is only key-material-adjacent, but this repo is public,
# so it stays out too):
#
#   aws ssm put-parameter --type SecureString --name /backup/passphrase --value ...
#   aws ssm put-parameter --type SecureString --name /backup/alerts-slack-webhook --value ...
#   aws ssm put-parameter --type SecureString --name /restore-check-db/sentry-cron-url --value ...
#
# The Sentry cron monitor defined below is the check's dead-man switch:
# db-lambda.py checks in against it, and Sentry alerts when a run is
# missed, times out, or fails. The check image is built and pushed with
# `just restore-check-db-image`; the task definition tracks :latest, so a
# push alone deploys a change.

locals {
  db_name          = "restore-check-db"
  db_log_group     = "/restore-check/db"
  db_stream_prefix = "task"
  backup_bucket    = "anika-database-backups"

  parameter_arn_prefix = "arn:aws:ssm:${local.region}:${data.aws_caller_identity.current.account_id}:parameter"
  webhook_parameter    = "/backup/alerts-slack-webhook"
  passphrase_parameter = "/backup/passphrase"
  sentry_parameter     = "/restore-check-db/sentry-cron-url"

  sentry_organization = "anika-legal"
  sentry_project      = "clerk"
}

# --- Task networking: no ingress at all, egress for S3/ECR/logs --------------

resource "aws_security_group" "db_task" {
  name        = "restore-check-db-task"
  description = "Restore check task: no ingress, egress only"
  vpc_id      = data.aws_vpc.default.id
}

resource "aws_vpc_security_group_egress_rule" "db_task_all_out" {
  security_group_id = aws_security_group.db_task.id
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}

# --- Image registry and run log ----------------------------------------------

resource "aws_ecr_repository" "db" {
  name = local.db_name
}

resource "aws_ecr_lifecycle_policy" "db" {
  repository = aws_ecr_repository.db.name
  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep only the most recent images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 5
      }
      action = { type = "expire" }
    }]
  })
}

resource "aws_cloudwatch_log_group" "db" {
  name              = local.db_log_group
  retention_in_days = 90
}

# --- The check task -----------------------------------------------------------

resource "aws_ecs_cluster" "db" {
  name = local.db_name
}

data "aws_iam_policy_document" "ecs_tasks_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

# What the running check may do: read the backup bucket, nothing else. It
# cannot even re-read the passphrase - that arrives only as an injected
# environment variable, fetched by the ECS agent under the execution role.
resource "aws_iam_role" "db_task" {
  name               = "restore-check-db-task"
  assume_role_policy = data.aws_iam_policy_document.ecs_tasks_assume.json
}

data "aws_iam_policy_document" "db_task" {
  statement {
    sid       = "ListBackupBucket"
    actions   = ["s3:ListBucket"]
    resources = ["arn:aws:s3:::${local.backup_bucket}"]
  }

  statement {
    sid       = "ReadBackupObjects"
    actions   = ["s3:GetObject"]
    resources = ["arn:aws:s3:::${local.backup_bucket}/*"]
  }
}

resource "aws_iam_role_policy" "db_task" {
  name   = "restore-check-db-task"
  role   = aws_iam_role.db_task.id
  policy = data.aws_iam_policy_document.db_task.json
}

# What the ECS agent does on the task's behalf: pull the image, deliver
# logs, and inject the passphrase (the default aws/ssm KMS key needs no
# explicit grant).
resource "aws_iam_role" "db_execution" {
  name               = "restore-check-db-execution"
  assume_role_policy = data.aws_iam_policy_document.ecs_tasks_assume.json
}

data "aws_iam_policy_document" "db_execution" {
  statement {
    sid       = "EcrAuth"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }

  statement {
    sid = "PullCheckImage"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:BatchGetImage",
      "ecr:GetDownloadUrlForLayer",
    ]
    resources = [aws_ecr_repository.db.arn]
  }

  statement {
    sid       = "DeliverTaskLogs"
    actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["${aws_cloudwatch_log_group.db.arn}:*"]
  }

  statement {
    sid       = "InjectPassphrase"
    actions   = ["ssm:GetParameter", "ssm:GetParameters"]
    resources = ["${local.parameter_arn_prefix}${local.passphrase_parameter}"]
  }
}

resource "aws_iam_role_policy" "db_execution" {
  name   = "restore-check-db-execution"
  role   = aws_iam_role.db_execution.id
  policy = data.aws_iam_policy_document.db_execution.json
}

resource "aws_ecs_task_definition" "db" {
  family                   = local.db_name
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "1024"
  memory                   = "4096"
  task_role_arn            = aws_iam_role.db_task.arn
  execution_role_arn       = aws_iam_role.db_execution.arn

  container_definitions = jsonencode([{
    name      = local.db_name
    image     = "${aws_ecr_repository.db.repository_url}:latest"
    essential = true

    # A proper init as PID 1: clean signal forwarding and reaping under
    # the timeout entrypoint.
    linuxParameters = { initProcessEnabled = true }

    environment = [
      { name = "S3_BUCKET", value = "s3://${local.backup_bucket}" },
      { name = "AWS_DEFAULT_REGION", value = local.region },
    ]

    secrets = [{
      name      = "BACKUP_PASSPHRASE"
      valueFrom = "${local.parameter_arn_prefix}${local.passphrase_parameter}"
    }]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.db.name
        awslogs-region        = local.region
        awslogs-stream-prefix = local.db_stream_prefix
      }
    }
  }])
}

# --- The orchestrating Lambda durable function --------------------------------

data "archive_file" "db_lambda" {
  type        = "zip"
  output_path = "${path.module}/builds/restore-check-db.zip"

  # db-lambda.py becomes db_lambda.py: module names cannot contain hyphens.
  source {
    content  = file("${path.module}/../../../restore-check/db-lambda.py")
    filename = "db_lambda.py"
  }

  source {
    content  = file("${path.module}/../../../restore-check/report.py")
    filename = "report.py"
  }
}

resource "aws_iam_role" "db_lambda" {
  name = "restore-check-db-lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

# Checkpoint operations for durable execution, plus the usual log-writing
# permissions (attached separately in case the durable policy ever drops
# them).
resource "aws_iam_role_policy_attachment" "db_lambda_durable" {
  role       = aws_iam_role.db_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicDurableExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "db_lambda_logs" {
  role       = aws_iam_role.db_lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy_document" "db_lambda" {
  statement {
    sid       = "RunCheckTask"
    actions   = ["ecs:RunTask"]
    resources = ["arn:aws:ecs:${local.region}:${data.aws_caller_identity.current.account_id}:task-definition/${local.db_name}:*"]
    condition {
      test     = "ArnEquals"
      variable = "ecs:cluster"
      values   = [aws_ecs_cluster.db.arn]
    }
  }

  statement {
    sid       = "ManageCheckTasks"
    actions   = ["ecs:StopTask", "ecs:DescribeTasks"]
    resources = ["arn:aws:ecs:${local.region}:${data.aws_caller_identity.current.account_id}:task/${local.db_name}/*"]
  }

  statement {
    sid       = "ListCheckTasks"
    actions   = ["ecs:ListTasks"]
    resources = ["*"]
    condition {
      test     = "ArnEquals"
      variable = "ecs:cluster"
      values   = [aws_ecs_cluster.db.arn]
    }
  }

  statement {
    sid       = "PassTaskRoles"
    actions   = ["iam:PassRole"]
    resources = [aws_iam_role.db_task.arn, aws_iam_role.db_execution.arn]
    condition {
      test     = "StringEquals"
      variable = "iam:PassedToService"
      values   = ["ecs-tasks.amazonaws.com"]
    }
  }

  statement {
    sid       = "ReadCheckResults"
    actions   = ["logs:GetLogEvents"]
    resources = ["${aws_cloudwatch_log_group.db.arn}:log-stream:*"]
  }

  statement {
    sid     = "ReadReportingParameters"
    actions = ["ssm:GetParameter"]
    resources = [
      "${local.parameter_arn_prefix}${local.webhook_parameter}",
      "${local.parameter_arn_prefix}${local.sentry_parameter}",
    ]
  }
}

resource "aws_iam_role_policy" "db_lambda" {
  name   = "restore-check-db-lambda"
  role   = aws_iam_role.db_lambda.id
  policy = data.aws_iam_policy_document.db_lambda.json
}

resource "aws_lambda_function" "db" {
  function_name    = local.db_name
  role             = aws_iam_role.db_lambda.arn
  filename         = data.archive_file.db_lambda.output_path
  source_code_hash = data.archive_file.db_lambda.output_base64sha256
  handler          = "db_lambda.handler"
  runtime          = "python3.13"
  timeout          = 300 # per invocation; the execution spans many
  memory_size      = 256

  # Durable functions must be invoked via a qualified ARN, so every apply
  # publishes a version and the live alias tracks it.
  publish = true

  durable_config {
    execution_timeout = 7200 # the outermost failsafe layer, see db-lambda.py
    retention_period  = 30   # days of execution history in the console
  }

  environment {
    variables = {
      CLUSTER           = aws_ecs_cluster.db.name
      TASK_DEFINITION   = aws_ecs_task_definition.db.family # latest ACTIVE revision
      SUBNET_ID         = local.subnet_id
      SECURITY_GROUP_ID = aws_security_group.db_task.id
      LOG_GROUP         = aws_cloudwatch_log_group.db.name
      CONTAINER_NAME    = local.db_name
      STREAM_PREFIX     = local.db_stream_prefix
      WEBHOOK_PARAMETER = local.webhook_parameter
      SENTRY_PARAMETER  = local.sentry_parameter
    }
  }
}

resource "aws_lambda_alias" "db_live" {
  name             = "live"
  function_name    = aws_lambda_function.db.function_name
  function_version = aws_lambda_function.db.version
}

# A failed execution is not retried by the async machinery: it would start
# a second, duplicate execution. Failures alert via the except handler and
# the Sentry monitor instead.
resource "aws_lambda_function_event_invoke_config" "db_live" {
  function_name          = aws_lambda_function.db.function_name
  qualifier              = aws_lambda_alias.db_live.name
  maximum_retry_attempts = 0
}

# --- The monthly schedule ------------------------------------------------------

resource "aws_scheduler_schedule_group" "restore_check" {
  name = "restore-check"
}

resource "aws_iam_role" "db_scheduler" {
  name = "restore-check-db-scheduler"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "scheduler.amazonaws.com" }
      Condition = {
        StringEquals = { "aws:SourceAccount" = data.aws_caller_identity.current.account_id }
      }
    }]
  })
}

data "aws_iam_policy_document" "db_scheduler" {
  statement {
    sid       = "InvokeCheckLambda"
    actions   = ["lambda:InvokeFunction"]
    resources = [aws_lambda_alias.db_live.arn]
  }
}

resource "aws_iam_role_policy" "db_scheduler" {
  name   = "restore-check-db-scheduler"
  role   = aws_iam_role.db_scheduler.id
  policy = data.aws_iam_policy_document.db_scheduler.json
}

resource "aws_scheduler_schedule" "db" {
  name       = local.db_name
  group_name = aws_scheduler_schedule_group.restore_check.name

  # Monthly, an hour or two after the nightly backup (2AM AEST) whatever
  # the DST offset - unlike a UTC cron, which drifts an hour across it.
  schedule_expression          = "cron(0 4 1 * ? *)"
  schedule_expression_timezone = "Australia/Melbourne"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = aws_lambda_alias.db_live.arn
    role_arn = aws_iam_role.db_scheduler.arn
    input    = jsonencode({})

    # Retries here cover only failed delivery of the invoke (the function
    # handles its own failures); a stale event is worthless, so cap the age.
    retry_policy {
      maximum_retry_attempts       = 3
      maximum_event_age_in_seconds = 3600
    }
  }
}

# --- The dead-man switch: a Sentry cron monitor --------------------------------

# db-lambda.py checks in against this monitor (in_progress on launch,
# ok/error on finish), so Sentry alerts when the check never starts, dies
# mid-run, or fails - deliberately outside AWS, so it does not share fate
# with what it watches. Its schedule mirrors aws_scheduler_schedule.db
# above: change both together. (A CloudWatch alarm cannot do this job -
# alarm evaluation ranges cap at 7 days, well short of a month.)
resource "sentry_cron_monitor" "db" {
  organization = local.sentry_organization
  project      = local.sentry_project
  name         = local.db_name

  schedule = {
    crontab = "0 4 1 * *"
  }
  timezone = "Australia/Melbourne"

  checkin_margin_minutes  = 120 # grace before a run counts as missed
  max_runtime_minutes     = 240 # in_progress older than this has died
  failure_issue_threshold = 1
  recovery_threshold      = 1
}

resource "sentry_alert" "db" {
  organization      = local.sentry_organization
  name              = local.db_name
  monitor_ids       = [sentry_cron_monitor.db.id]
  frequency_minutes = 1440

  trigger_conditions = [
    { first_seen_event = {} },
    { regression_event = {} },
  ]

  action_filters = [{
    logic_type = "all"
    actions = [{
      email = {
        target_type      = "issue_owners"
        fallthrough_type = "AllMembers"
      }
    }]
  }]
}
