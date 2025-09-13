module "storage" {
  source = "./modules/storage"
  rg_name = var.rg_name
  location = var.location
  sa_name = var.sa_name
  container_name = var.container_name
}

module "acr" {
  source = "./modules/acr"
  rg_name = var.rg_name
  location = var.location
  acr_name = var.acr_name
}

module "aci" {
  source = "./modules/aci"
  rg_name = var.rg_name
  location = var.location
  aci_name = var.aci_name
  acr_login_server = module.acr.acr_login_server
  image = var.image
  storage_account_name = module.storage.storage_account_name
}

