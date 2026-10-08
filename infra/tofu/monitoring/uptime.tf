locals {
  checks = {
    website     = { name = "Website", project = "clerk", host = "site", path = "/" }
    clerk_login = { name = "Clerk login", project = "clerk", host = "site", path = "/accounts/login/" }
    health      = { name = "Health check", project = "clerk", host = "site", path = "/health/" }
    intake_form = { name = "Intake form", project = "intake", host = "intake", path = "/" }
  }

  # One monitor per environment and check, keyed "production/website".
  monitors = {
    for pair in setproduct(keys(local.environments), keys(local.checks)) :
    "${pair[0]}/${pair[1]}" => {
      environment = pair[0]
      name        = "${local.checks[pair[1]].name} (${pair[0]})"
      project     = local.checks[pair[1]].project
      url         = "https://${local.environments[pair[0]].hosts[local.checks[pair[1]].host]}${local.checks[pair[1]].path}"
    }
  }
}

resource "sentry_uptime_monitor" "this" {
  for_each = local.monitors

  organization       = local.organization
  project            = each.value.project
  name               = each.value.name
  environment        = each.value.environment
  url                = each.value.url
  method             = "GET"
  interval_seconds   = 60
  timeout_ms         = 10000
  downtime_threshold = 3
  recovery_threshold = 1
}

resource "sentry_alert" "uptime" {
  for_each = local.environments

  organization      = local.organization
  name              = "Uptime: down or recovered (${each.key})"
  frequency_minutes = 0
  monitor_ids = [
    for key, monitor in sentry_uptime_monitor.this : monitor.id
    if local.monitors[key].environment == each.key
  ]

  # A repeat outage reopens the same issue, so regressions are outages too.
  trigger_conditions = [
    { first_seen_event = {} },
    { reappeared_event = {} },
    { regression_event = {} },
    { issue_resolved_trigger = {} },
  ]

  action_filters = [{
    logic_type = "all"
    actions = [
      {
        slack = {
          integration_id = data.sentry_organization_integration.slack.id
          channel_name   = each.value.slack_channel.name
          channel_id     = each.value.slack_channel.id
        }
      },
      {
        email = {
          target_type = "user"
          target_id   = local.tech_user_id
        }
      },
    ]
  }]
}
