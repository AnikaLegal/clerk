# The Azure spend tripwire: emails tech@ when the month's actual spend
# crosses 80% and 100% of the limit, and when Azure forecasts the month will
# exceed it. The amount is in the billing account's currency. It covers
# what the Sentinel trial does not, such as automation, and everything once
# the trial ends.

data "azurerm_subscription" "current" {}

resource "azurerm_consumption_budget_subscription" "monthly" {
  name            = "azure-monthly"
  subscription_id = data.azurerm_subscription.current.id
  amount          = 50
  time_grain      = "Monthly"

  time_period {
    start_date = "2026-10-01T00:00:00Z"
  }

  notification {
    operator       = "GreaterThan"
    threshold      = 80
    threshold_type = "Actual"
    contact_emails = [local.alert_email]
  }

  notification {
    operator       = "GreaterThan"
    threshold      = 100
    threshold_type = "Actual"
    contact_emails = [local.alert_email]
  }

  notification {
    operator       = "GreaterThan"
    threshold      = 100
    threshold_type = "Forecasted"
    contact_emails = [local.alert_email]
  }
}
