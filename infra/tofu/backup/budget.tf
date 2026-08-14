# The AWS Backup spend tripwire: emails tech@ when the month's actual
# spend crosses 80% and 100% of the limit, and when AWS forecasts the
# month will exceed it. Imported from the console-built original in
# August 2026, raising the limit from $45: the monthly restore testing
# added in TEC-2063 legitimately spends ~$5 on the 1st (~$1 per test
# restore plus restored data, more in the quarters when the Melbourne
# air-gapped vault is tested too), on top of a ~$26 storage baseline.
#
# Expect the FORECASTED alert to be the noisy one: AWS extrapolates
# recent days, so the 1st-of-month restore testing spike (or a rehearsal
# week) can project a wildly inflated month. It is kept anyway as the
# earliest possible drift warning - check the daily costs before acting
# on it.

resource "aws_budgets_budget" "backup_monthly" {
  name         = "aws-backup-monthly"
  budget_type  = "COST"
  limit_amount = "60.0"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  time_period_start = "2026-07-01_00:00"

  cost_filter {
    name   = "Service"
    values = ["AWS Backup"]
  }

  notification {
    notification_type          = "ACTUAL"
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    subscriber_email_addresses = ["tech@anikalegal.com"]
  }

  notification {
    notification_type          = "ACTUAL"
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    subscriber_email_addresses = ["tech@anikalegal.com"]
  }

  notification {
    notification_type          = "FORECASTED"
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    subscriber_email_addresses = ["tech@anikalegal.com"]
  }
}

import {
  to = aws_budgets_budget.backup_monthly
  id = "330608907609:aws-backup-monthly"
}
