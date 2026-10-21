# Sentinel itself and the Microsoft connectors that can be managed as code.
# The Google Workspace connector and the Content hub solutions (rule
# templates, workbooks) are set up in the Defender portal.

resource "azurerm_sentinel_log_analytics_workspace_onboarding" "this" {
  count = local.sentinel_enabled ? 1 : 0

  workspace_id = azurerm_log_analytics_workspace.sentinel.id
}

# Exchange, SharePoint (including OneDrive) and Teams audit records, which
# Sentinel ingests free.
resource "azurerm_sentinel_data_connector_office_365" "this" {
  count = local.sentinel_enabled ? 1 : 0

  name                       = "microsoft-365"
  log_analytics_workspace_id = azurerm_sentinel_log_analytics_workspace_onboarding.this[0].workspace_id
  exchange_enabled           = true
  sharepoint_enabled         = true
  teams_enabled              = true
}

# Entra ID's export to the workspace. Sign-in categories need Entra ID P1 in
# the tenant.
resource "azurerm_monitor_aad_diagnostic_setting" "sentinel" {
  count = local.sentinel_enabled ? 1 : 0

  name                       = "sentinel"
  log_analytics_workspace_id = azurerm_sentinel_log_analytics_workspace_onboarding.this[0].workspace_id

  dynamic "enabled_log" {
    for_each = toset([
      "AuditLogs",
      "SignInLogs",
      "NonInteractiveUserSignInLogs",
      "ServicePrincipalSignInLogs",
      "ManagedIdentitySignInLogs",
    ])

    content {
      category = enabled_log.value
    }
  }
}
