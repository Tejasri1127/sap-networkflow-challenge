terraform {
  required_version = ">= 1.1"
  backend "azurerm" {
    resource_group_name  = "tfstate-rg"
    storage_account_name = "tfstateaccount"
    container_name       = "tfstate"
    key                  = "sap-networkflow-terraform.tfstate"
  }
}

