resource "azurerm_container_group" "aci" {
  name                = var.aci_name
  resource_group_name = var.rg_name
  location            = var.location
  os_type             = "Linux"

  ip_address_type     = "Public"
  dns_name_label      = var.aci_name
  container {
    name   = var.aci_name
    image  = var.image
    cpu    = 0.5
    memory = 1.5
    ports {
      port     = 8050
      protocol = "TCP"
    }
    environment_variables = {
      AZURE_STORAGE_ACCOUNT = var.storage_account_name
    }
  }
}
output "aci_fqdn" { value = azurerm_container_group.aci.fqdn }

