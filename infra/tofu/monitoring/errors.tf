# The projects whose new issues the error alerts cover.
data "sentry_project_issue_stream_monitor" "this" {
  for_each = toset(["clerk", "intake", "clerk-frontend"])

  organization = local.organization
  project      = each.key
}

resource "sentry_alert" "errors" {
  for_each = local.environments

  organization      = local.organization
  name              = "Errors: new issue (${each.key})"
  environment       = each.key
  frequency_minutes = 30
  monitor_ids       = [for monitor in data.sentry_project_issue_stream_monitor.this : monitor.id]

  trigger_conditions = [
    { first_seen_event = {} },
  ]

  action_filters = [
    {
      logic_type = "all"
      actions = [{
        sentry_app = {
          sentry_app_id = local.linear_app_id
          settings = [
            { name = "teamId", value = local.linear_team_id },
            { name = "assigneeId", value = "" },
            { name = "labelId", value = each.value.linear_label_id },
            { name = "projectId", value = "" },
            { name = "stateId", value = local.linear_state_id },
          ]
        }
      }]
    },
    {
      # Outages are posted by the uptime alerts; they only get the Linear issue here.
      logic_type = "all"
      conditions = [{
        issue_type = {
          value   = "uptime_domain_failure"
          include = false
        }
      }]
      actions = [{
        slack = {
          integration_id = data.sentry_organization_integration.slack.id
          channel_name   = each.value.slack_channel.name
          channel_id     = each.value.slack_channel.id
        }
      }]
    },
  ]
}
