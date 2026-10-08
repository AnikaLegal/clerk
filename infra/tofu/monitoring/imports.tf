# Adopts the monitors and alerts first made in the Sentry UI. Delete this
# file once it has been applied.

locals {
  imported_monitor_ids = {
    "production/website"     = "10574042"
    "production/clerk_login" = "10574043"
    "production/health"      = "10574044"
    "production/intake_form" = "10574045"
    "staging/website"        = "10574047"
    "staging/clerk_login"    = "10574049"
    "staging/health"         = "10574050"
    "staging/intake_form"    = "10574051"
  }
  imported_uptime_alert_ids = {
    production = "6133831"
    staging    = "6135267"
  }
  imported_error_alert_ids = {
    production = "577437"
    staging    = "577436"
  }
}

import {
  for_each = local.imported_monitor_ids
  to       = sentry_uptime_monitor.this[each.key]
  id       = "${local.organization}/${local.monitors[each.key].project}/${each.value}"
}

import {
  for_each = local.imported_uptime_alert_ids
  to       = sentry_alert.uptime[each.key]
  id       = "${local.organization}/${each.value}"
}

import {
  for_each = local.imported_error_alert_ids
  to       = sentry_alert.errors[each.key]
  id       = "${local.organization}/${each.value}"
}
