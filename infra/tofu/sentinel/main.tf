# Microsoft Sentinel for collecting, retaining and alerting on Google
# Workspace, Microsoft 365 and Entra ID audit logs (TEC-2199). Applied by a
# human signed in to Azure as the subscription Owner (Global Administrator
# in Entra for the connectors), with AWS credentials for the state bucket
# (see ../README.md):
#
#   az login
#   export ARM_SUBSCRIPTION_ID=...
#   tofu -chdir=infra/tofu/sentinel init
#   tofu -chdir=infra/tofu/sentinel apply
#
# The subscription ID comes from the environment so it stays out of this
# public repo.

terraform {
  required_version = ">= 1.10"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }

  backend "s3" {
    bucket       = "anika-terraform-state"
    key          = "sentinel/terraform.tfstate"
    region       = "ap-southeast-2"
    use_lockfile = true
  }
}

provider "azurerm" {
  features {}

  resource_providers_to_register = [
    "Microsoft.OperationalInsights",
    "Microsoft.OperationsManagement",
    "Microsoft.SecurityInsights",
  ]
}

locals {
  # Australia East is the only Australian region with the Sentinel data lake.
  location = "australiaeast"

  alert_email = "tech@anikalegal.org.au"

  # Turning Sentinel on starts its 31-day free trial, and anything ingested
  # before then is billed at Log Analytics rates, so the onboarding and every
  # connector wait on this. Flip it on the day the sources are connected.
  sentinel_enabled = false
}

resource "azurerm_resource_group" "sentinel" {
  name     = "sentinel"
  location = local.location
}

resource "azurerm_log_analytics_workspace" "sentinel" {
  name                = "anika-sentinel"
  location            = azurerm_resource_group.sentinel.location
  resource_group_name = azurerm_resource_group.sentinel.name
  sku                 = "PerGB2018"

  # Sentinel includes 90 days of analytics-tier retention at no charge.
  retention_in_days = 90

  # A guard against runaway ingestion, well above the expected volume.
  # Ingestion stops for the rest of the day once it is reached.
  daily_quota_gb = 5

  # Shared keys would sit usable in state and let anyone holding one write
  # events into the workspace; connectors authenticate with Entra instead.
  local_authentication_enabled = false
}
