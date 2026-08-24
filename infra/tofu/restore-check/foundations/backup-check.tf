# The daily S3 backup landing check (TEC-2063): a small Lambda that
# asserts every protected bucket has a fresh AWS Backup recovery point in
# the primary vault AND that the copy landed in the air-gapped Melbourne
# vault. Gaps alert Slack; the backup-check-s3 Sentry cron monitor is the
# dead-man behind the Lambda itself. This is the "backups exist" layer;
# s3.tf is the "backups restore" layer.
#
# Its SecureString parameter is created by hand, like the others:
#
#   aws ssm put-parameter --type SecureString --name /backup-check-s3/sentry-cron-url --value ...

# The protected-bucket list and vault ARNs come from the infra/tofu/backup
# root - the selection there is the single source of truth for what "all
# protected buckets" means.
data "terraform_remote_state" "backup" {
  backend = "s3"

  config = {
    bucket = "anika-terraform-state"
    key    = "backup/terraform.tfstate"
    region = local.region
  }
}

locals {
  backup_check_name      = "backup-check-s3"
  backup_check_parameter = "/backup-check-s3/sentry-cron-url"

  # The backup plan stamps its daily recovery points 5AM Melbourne, but
  # the jobs take hours to COMPLETE (anika-twilio-audio routinely finishes
  # ~9:30AM), so the 9AM check must not race the same-day job. The
  # contract is that YESTERDAY's point - exactly 28h old at check time -
  # has landed, with margin on top for jitter; a genuinely missed backup
  # still alerts within a day, when the newest point reaches ~52h. The
  # copy gets a little longer for its lag behind the snapshot.
  backup_check_schedule   = "0 9 * * *" # crontab (Sentry) form
  primary_threshold_hours = 30
  copy_threshold_hours    = 32
}

# --- The Lambda ------------------------------------------------------------------

data "archive_file" "backup_check_lambda" {
  type        = "zip"
  output_path = "${path.module}/builds/backup-check-s3.zip"

  source {
    content  = file("${path.module}/../../../restore-check/backup-check-lambda.py")
    filename = "backup_check_lambda.py"
  }
}

resource "aws_iam_role" "backup_check" {
  name = "backup-check-s3-lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "backup_check_logs" {
  role       = aws_iam_role.backup_check.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy_document" "backup_check" {
  statement {
    sid       = "ListRecoveryPoints"
    actions   = ["backup:ListRecoveryPointsByResource"]
    resources = ["*"]
  }

  statement {
    sid     = "ReadReportingParameters"
    actions = ["ssm:GetParameter"]
    resources = [
      "${local.parameter_arn_prefix}${local.webhook_parameter}",
      "${local.parameter_arn_prefix}${local.backup_check_parameter}",
    ]
  }
}

resource "aws_iam_role_policy" "backup_check" {
  name   = "backup-check-s3-lambda"
  role   = aws_iam_role.backup_check.id
  policy = data.aws_iam_policy_document.backup_check.json
}

resource "aws_lambda_function" "backup_check" {
  function_name    = local.backup_check_name
  role             = aws_iam_role.backup_check.arn
  filename         = data.archive_file.backup_check_lambda.output_path
  source_code_hash = data.archive_file.backup_check_lambda.output_base64sha256
  handler          = "backup_check_lambda.handler"
  runtime          = "python3.13"
  timeout          = 120
  memory_size      = 128

  environment {
    variables = {
      PROTECTED_BUCKETS       = jsonencode(data.terraform_remote_state.backup.outputs.protected_buckets)
      PRIMARY_REGION          = local.region
      COPY_REGION             = "ap-southeast-4"
      PRIMARY_THRESHOLD_HOURS = local.primary_threshold_hours
      COPY_THRESHOLD_HOURS    = local.copy_threshold_hours
      WEBHOOK_PARAMETER       = local.webhook_parameter
      SENTRY_PARAMETER        = local.backup_check_parameter
    }
  }
}

# --- The daily schedule -----------------------------------------------------------

resource "aws_iam_role" "backup_check_scheduler" {
  name = "backup-check-s3-scheduler"

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

data "aws_iam_policy_document" "backup_check_scheduler" {
  statement {
    sid       = "InvokeBackupCheckLambda"
    actions   = ["lambda:InvokeFunction"]
    resources = [aws_lambda_function.backup_check.arn]
  }
}

resource "aws_iam_role_policy" "backup_check_scheduler" {
  name   = "backup-check-s3-scheduler"
  role   = aws_iam_role.backup_check_scheduler.id
  policy = data.aws_iam_policy_document.backup_check_scheduler.json
}

resource "aws_scheduler_schedule" "backup_check" {
  name       = local.backup_check_name
  group_name = aws_scheduler_schedule_group.restore_check.name

  schedule_expression          = "cron(0 9 * * ? *)"
  schedule_expression_timezone = "Australia/Melbourne"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = aws_lambda_function.backup_check.arn
    role_arn = aws_iam_role.backup_check_scheduler.arn
    input    = jsonencode({})

    retry_policy {
      maximum_retry_attempts       = 3
      maximum_event_age_in_seconds = 3600
    }
  }
}

# --- The dead-man switch: a Sentry cron monitor ------------------------------------

# The Lambda checks in ok/error daily; Sentry alerts when a check-in is
# missed (the Lambda silently stopped) or reports error. The schedule
# mirrors aws_scheduler_schedule.backup_check above: change both together.
resource "sentry_cron_monitor" "backup_check" {
  organization = local.sentry_organization
  project      = local.sentry_project
  name         = local.backup_check_name

  schedule = {
    crontab = local.backup_check_schedule
  }
  timezone = "Australia/Melbourne"

  checkin_margin_minutes  = 120
  max_runtime_minutes     = 30
  failure_issue_threshold = 1
  recovery_threshold      = 1
}

resource "sentry_alert" "backup_check" {
  organization      = local.sentry_organization
  name              = local.backup_check_name
  monitor_ids       = [sentry_cron_monitor.backup_check.id]
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
