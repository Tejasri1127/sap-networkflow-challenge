resource "azurerm_resource_group" "rg" {
  name     = var.rg_name
  location = var.location
}

resource "azurerm_storage_account" "sa" {
  name                     = var.sa_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "logs" {
  name                 = var.container_name
  storage_account_name = azurerm_storage_account.sa.name
  container_access_type = "private"
}

output "storage_account_name" { value = azurerm_storage_account.sa.name }
output "container_name" { value = azurerm_storage_container.logs.name }

