# The S3 restore testing check (TEC-2063): AWS Backup restore testing
# plans restore every protected bucket's latest recovery point into a
# scratch bucket (awsbackup-restore-test-*, created and later deleted by
# the service), the restore-check-s3-validate Lambda proves the restored
# content against the live bucket and stamps a verdict on each job, and
# the restore-check-s3-report durable Lambda posts one Slack table and
# asserts every bucket was actually tested. The Sydney vault is tested
# monthly; the air-gapped Melbourne vault quarterly. See
# docs/restore-check.md and infra/restore-check/s3-*-lambda.py.
#
# Melbourne resources live in this same root via the per-resource region
# attribute; restore jobs run where the recovery point is, so Melbourne
# gets its own plan and an EventBridge rule that forwards its completion
# events to the Sydney bus, where the single validate Lambda serves both.
#
# Its SecureString parameter is created by hand, like the others:
#
#   aws ssm put-parameter --type SecureString --name /restore-check-s3/sentry-cron-url --value ...

locals {
  s3_name             = "restore-check-s3"
  s3_sentry_parameter = "/restore-check-s3/sentry-cron-url"

  airgap_region = "ap-southeast-4"
  airgap_months = [1, 4, 7, 10] # quarterly, aligned to the Sydney monthly run

  protected_bucket_arns = [
    for bucket in data.terraform_remote_state.backup.outputs.protected_buckets :
    "arn:aws:s3:::${bucket}"
  ]

  # Restore testing names its scratch resources with this fixed prefix;
  # the restore role and the validate Lambda are scoped to it.
  scratch_bucket_arn = "arn:aws:s3:::awsbackup-restore-test-*"

  # The reporter runs at noon: the plans start their jobs at 5-6AM, so by
  # then most restores are validated and the durable wait mops up the rest.
  s3_report_schedule = "0 12 1 * *" # crontab (Sentry) form
}

# The Sydney vault's CMK: the restore role must be able to decrypt the
# recovery points it restores from. (The air-gapped vault uses an
# AWS-owned key, which needs no grant.)
data "aws_backup_vault" "clerk" {
  name = "anika-clerk-backup-vault"
}

# --- The restore role -----------------------------------------------------------

# What AWS Backup assumes to run the test restores: the actions of the
# AWSBackupServiceRolePolicyForS3Restore managed policy, scoped from
# arn:aws:s3:::* down to the scratch buckets restore testing creates.
resource "aws_iam_role" "s3_restore" {
  name = "restore-check-s3-restore"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "backup.amazonaws.com" }
      Condition = {
        StringEquals = { "aws:SourceAccount" = data.aws_caller_identity.current.account_id }
      }
    }]
  })
}

data "aws_iam_policy_document" "s3_restore" {
  statement {
    sid = "CreateScratchBuckets"
    actions = [
      "s3:CreateBucket",
      "s3:ListBucket",
      "s3:ListBucketVersions",
      "s3:GetBucketVersioning",
      "s3:GetBucketLocation",
      "s3:PutBucketVersioning",
      "s3:GetBucketOwnershipControls",
      "s3:PutBucketOwnershipControls",
    ]
    resources = [local.scratch_bucket_arn]
  }

  statement {
    sid = "WriteScratchObjects"
    actions = [
      "s3:GetObject",
      "s3:GetObjectVersion",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:GetObjectAcl",
      "s3:PutObjectAcl",
      "s3:GetObjectVersionAcl",
      "s3:PutObjectVersionAcl",
      "s3:GetObjectTagging",
      "s3:PutObjectTagging",
      "s3:ListMultipartUploadParts",
    ]
    resources = ["${local.scratch_bucket_arn}/*"]
  }

  statement {
    sid       = "DecryptRecoveryPoints"
    actions   = ["kms:Decrypt", "kms:DescribeKey"]
    resources = [data.aws_backup_vault.clerk.kms_key_arn]
  }

  statement {
    sid       = "UseKeysViaS3"
    actions   = ["kms:Decrypt", "kms:DescribeKey", "kms:GenerateDataKey"]
    resources = ["*"]
    condition {
      test     = "StringLike"
      variable = "kms:ViaService"
      values   = ["s3.*.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy" "s3_restore" {
  name   = "restore-check-s3-restore"
  role   = aws_iam_role.s3_restore.id
  policy = data.aws_iam_policy_document.s3_restore.json
}

# --- The restore testing plans ---------------------------------------------------

# Restore testing plan names only allow alphanumerics and underscores,
# hence the departure from the hyphenated naming everywhere else.
resource "aws_backup_restore_testing_plan" "s3" {
  name                         = "restore_check_s3"
  schedule_expression          = "cron(0 5 1 * ? *)" # monthly, after the 4AM db check
  schedule_expression_timezone = "Australia/Melbourne"
  start_window_hours           = 1

  recovery_point_selection {
    algorithm             = "LATEST_WITHIN_WINDOW"
    include_vaults        = [data.terraform_remote_state.backup.outputs.vault_arn]
    recovery_point_types  = ["SNAPSHOT"]
    selection_window_days = 7
  }
}

resource "aws_backup_restore_testing_selection" "s3" {
  name                      = "s3_buckets"
  restore_testing_plan_name = aws_backup_restore_testing_plan.s3.name
  protected_resource_type   = "S3"
  protected_resource_arns   = local.protected_bucket_arns
  iam_role_arn              = aws_iam_role.s3_restore.arn

  # The verdict usually lands within minutes of the restore completing;
  # the window is only how long AWS waits before cleanup if it never does.
  validation_window_hours = 24

  # Our backups carry ACLs (the media buckets rely on public-read), so
  # restore testing would try to restore them - into a scratch bucket
  # that blocks public ACLs. Skip them: ACL fidelity is not under test.
  restore_metadata_overrides = {
    restoreACLs = "false"
  }
}

resource "aws_backup_restore_testing_plan" "s3_airgap" {
  region = local.airgap_region

  name                         = "restore_check_s3_airgap"
  schedule_expression          = "cron(0 5 1 ${join(",", local.airgap_months)} ? *)"
  schedule_expression_timezone = "Australia/Melbourne"
  start_window_hours           = 1

  recovery_point_selection {
    algorithm             = "LATEST_WITHIN_WINDOW"
    include_vaults        = [data.terraform_remote_state.backup.outputs.air_gapped_vault_arn]
    recovery_point_types  = ["SNAPSHOT"]
    selection_window_days = 7
  }
}

resource "aws_backup_restore_testing_selection" "s3_airgap" {
  region = local.airgap_region

  name                      = "s3_buckets"
  restore_testing_plan_name = aws_backup_restore_testing_plan.s3_airgap.name
  protected_resource_type   = "S3"
  protected_resource_arns   = local.protected_bucket_arns
  iam_role_arn              = aws_iam_role.s3_restore.arn
  validation_window_hours   = 24

  restore_metadata_overrides = {
    restoreACLs = "false"
  }
}

# --- The validate Lambda ---------------------------------------------------------

data "archive_file" "s3_validate_lambda" {
  type        = "zip"
  output_path = "${path.module}/builds/restore-check-s3-validate.zip"

  source {
    content  = file("${path.module}/../../../restore-check/s3-validate-lambda.py")
    filename = "s3_validate_lambda.py"
  }
}

resource "aws_iam_role" "s3_validate" {
  name = "restore-check-s3-validate-lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "s3_validate_logs" {
  role       = aws_iam_role.s3_validate.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy_document" "s3_validate" {
  statement {
    sid = "StampRestoreJobs"
    actions = [
      "backup:DescribeRestoreJob",
      "backup:PutRestoreValidationResult",
    ]
    resources = ["*"]
  }

  statement {
    sid       = "ListComparedBuckets"
    actions   = ["s3:ListBucket"]
    resources = concat(local.protected_bucket_arns, [local.scratch_bucket_arn])
  }

  statement {
    sid       = "ReadRestoredObjects"
    actions   = ["s3:GetObject"]
    resources = ["${local.scratch_bucket_arn}/*"]
  }
}

resource "aws_iam_role_policy" "s3_validate" {
  name   = "restore-check-s3-validate-lambda"
  role   = aws_iam_role.s3_validate.id
  policy = data.aws_iam_policy_document.s3_validate.json
}

resource "aws_lambda_function" "s3_validate" {
  function_name    = "restore-check-s3-validate"
  role             = aws_iam_role.s3_validate.arn
  filename         = data.archive_file.s3_validate_lambda.output_path
  source_code_hash = data.archive_file.s3_validate_lambda.output_base64sha256
  handler          = "s3_validate_lambda.handler"
  runtime          = "python3.13"
  timeout          = 900  # full listings of the largest bucket, twice
  memory_size      = 1024 # both listings held in memory; ~44k objects today
}

# --- Wiring: completed restore jobs invoke the validator -------------------------

# The documented validation hook: Restore Job State Change / COMPLETED,
# filtered to our testing plans so manual restores never trigger it.
resource "aws_cloudwatch_event_rule" "s3_validate" {
  name        = "restore-check-s3-job-complete"
  description = "Validate completed S3 restore testing jobs"

  event_pattern = jsonencode({
    source      = ["aws.backup"]
    detail-type = ["Restore Job State Change"]
    detail = {
      status = ["COMPLETED"]
      restoreTestingPlanArn = [
        aws_backup_restore_testing_plan.s3.arn,
        aws_backup_restore_testing_plan.s3_airgap.arn,
      ]
    }
  })
}

resource "aws_cloudwatch_event_target" "s3_validate" {
  rule = aws_cloudwatch_event_rule.s3_validate.name
  arn  = aws_lambda_function.s3_validate.arn
}

resource "aws_lambda_permission" "s3_validate" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.s3_validate.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.s3_validate.arn
}

# Melbourne's events fire on Melbourne's bus; forward them to Sydney's so
# the one validate Lambda serves both regions (the verdict is stamped
# back in the job's own region via the event's region field).
resource "aws_cloudwatch_event_rule" "s3_validate_airgap" {
  region = local.airgap_region

  name        = "restore-check-s3-job-complete"
  description = "Forward completed S3 restore testing jobs to Sydney"

  event_pattern = jsonencode({
    source      = ["aws.backup"]
    detail-type = ["Restore Job State Change"]
    detail = {
      status                = ["COMPLETED"]
      restoreTestingPlanArn = [aws_backup_restore_testing_plan.s3_airgap.arn]
    }
  })
}

resource "aws_iam_role" "s3_event_forward" {
  name = "restore-check-s3-event-forward"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "events.amazonaws.com" }
      Condition = {
        StringEquals = { "aws:SourceAccount" = data.aws_caller_identity.current.account_id }
      }
    }]
  })
}

data "aws_iam_policy_document" "s3_event_forward" {
  statement {
    sid       = "ForwardToSydney"
    actions   = ["events:PutEvents"]
    resources = ["arn:aws:events:${local.region}:${data.aws_caller_identity.current.account_id}:event-bus/default"]
  }
}

resource "aws_iam_role_policy" "s3_event_forward" {
  name   = "restore-check-s3-event-forward"
  role   = aws_iam_role.s3_event_forward.id
  policy = data.aws_iam_policy_document.s3_event_forward.json
}

resource "aws_cloudwatch_event_target" "s3_validate_airgap" {
  region = local.airgap_region

  rule     = aws_cloudwatch_event_rule.s3_validate_airgap.name
  arn      = "arn:aws:events:${local.region}:${data.aws_caller_identity.current.account_id}:event-bus/default"
  role_arn = aws_iam_role.s3_event_forward.arn
}

# --- The reporting Lambda durable function ---------------------------------------

data "archive_file" "s3_report_lambda" {
  type        = "zip"
  output_path = "${path.module}/builds/restore-check-s3-report.zip"

  source {
    content  = file("${path.module}/../../../restore-check/s3-report-lambda.py")
    filename = "s3_report_lambda.py"
  }

  source {
    content  = file("${path.module}/../../../restore-check/report.py")
    filename = "report.py"
  }
}

resource "aws_iam_role" "s3_report" {
  name = "restore-check-s3-report-lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "s3_report_durable" {
  role       = aws_iam_role.s3_report.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicDurableExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "s3_report_logs" {
  role       = aws_iam_role.s3_report.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy_document" "s3_report" {
  statement {
    sid       = "ListRestoreJobs"
    actions   = ["backup:ListRestoreJobs"]
    resources = ["*"]
  }

  statement {
    sid     = "ReadReportingParameters"
    actions = ["ssm:GetParameter"]
    resources = [
      "${local.parameter_arn_prefix}${local.webhook_parameter}",
      "${local.parameter_arn_prefix}${local.s3_sentry_parameter}",
    ]
  }
}

resource "aws_iam_role_policy" "s3_report" {
  name   = "restore-check-s3-report-lambda"
  role   = aws_iam_role.s3_report.id
  policy = data.aws_iam_policy_document.s3_report.json
}

resource "aws_lambda_function" "s3_report" {
  function_name    = "restore-check-s3-report"
  role             = aws_iam_role.s3_report.arn
  filename         = data.archive_file.s3_report_lambda.output_path
  source_code_hash = data.archive_file.s3_report_lambda.output_base64sha256
  handler          = "s3_report_lambda.handler"
  runtime          = "python3.13"
  timeout          = 300 # per invocation; the execution spans many
  memory_size      = 256

  publish = true

  durable_config {
    execution_timeout = 28800 # the ~6h straggler wait, with headroom
    retention_period  = 30
  }

  environment {
    variables = {
      PRIMARY_PLAN_ARN  = aws_backup_restore_testing_plan.s3.arn
      PRIMARY_REGION    = local.region
      AIRGAP_PLAN_ARN   = aws_backup_restore_testing_plan.s3_airgap.arn
      AIRGAP_REGION     = local.airgap_region
      AIRGAP_MONTHS     = join(",", local.airgap_months)
      PROTECTED_BUCKETS = jsonencode(data.terraform_remote_state.backup.outputs.protected_buckets)
      WEBHOOK_PARAMETER = local.webhook_parameter
      SENTRY_PARAMETER  = local.s3_sentry_parameter
    }
  }
}

resource "aws_lambda_alias" "s3_report_live" {
  name             = "live"
  function_name    = aws_lambda_function.s3_report.function_name
  function_version = aws_lambda_function.s3_report.version
}

# As with the db check: a retry would start a duplicate execution.
resource "aws_lambda_function_event_invoke_config" "s3_report_live" {
  function_name          = aws_lambda_function.s3_report.function_name
  qualifier              = aws_lambda_alias.s3_report_live.name
  maximum_retry_attempts = 0
}

# --- The monthly reporting schedule -----------------------------------------------

resource "aws_iam_role" "s3_scheduler" {
  name = "restore-check-s3-scheduler"

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

data "aws_iam_policy_document" "s3_scheduler" {
  statement {
    sid       = "InvokeReportLambda"
    actions   = ["lambda:InvokeFunction"]
    resources = [aws_lambda_alias.s3_report_live.arn]
  }
}

resource "aws_iam_role_policy" "s3_scheduler" {
  name   = "restore-check-s3-scheduler"
  role   = aws_iam_role.s3_scheduler.id
  policy = data.aws_iam_policy_document.s3_scheduler.json
}

resource "aws_scheduler_schedule" "s3_report" {
  name       = local.s3_name
  group_name = aws_scheduler_schedule_group.restore_check.name

  schedule_expression          = "cron(0 12 1 * ? *)"
  schedule_expression_timezone = "Australia/Melbourne"

  flexible_time_window {
    mode = "OFF"
  }

  target {
    arn      = aws_lambda_alias.s3_report_live.arn
    role_arn = aws_iam_role.s3_scheduler.arn
    input    = jsonencode({})

    retry_policy {
      maximum_retry_attempts       = 3
      maximum_event_age_in_seconds = 3600
    }
  }
}

# --- The dead-man switch: a Sentry cron monitor ------------------------------------

# The reporter checks in against this monitor, so Sentry alerts when the
# whole restore testing pipeline silently stops as well as when a test
# fails. Its schedule mirrors aws_scheduler_schedule.s3_report above:
# change both together.
resource "sentry_cron_monitor" "s3" {
  organization = local.sentry_organization
  project      = local.sentry_project
  name         = local.s3_name

  schedule = {
    crontab = local.s3_report_schedule
  }
  timezone = "Australia/Melbourne"

  checkin_margin_minutes  = 120
  max_runtime_minutes     = 480 # the reporter may legitimately wait ~6h
  failure_issue_threshold = 1
  recovery_threshold      = 1
}

resource "sentry_alert" "s3" {
  organization      = local.sentry_organization
  name              = local.s3_name
  monitor_ids       = [sentry_cron_monitor.s3.id]
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
