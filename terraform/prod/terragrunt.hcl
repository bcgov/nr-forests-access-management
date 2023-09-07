include {
  path = find_in_parent_folders()
}

locals {
  common_vars = read_terragrunt_config(find_in_parent_folders("common_vars.hcl"))
}

generate "prod_tfvars" {
  path              = "prod.auto.tfvars"
  if_exists         = "overwrite"
  disable_signature = true
  contents          = <<-EOF
  fam_user_pool_name = "prod-fam-user-pool-bcsc"
  fam_user_pool_domain_name = "prod-fam-user-pool-domain"
  famdb_cluster_name = "prod-fam-cluster"
  oidc_idir_idp_client_id = "fsa-cognito-idir-dev-4088"
  oidc_idir_idp_issuer = "https://loginproxy.gov.bc.ca/auth/realms/standard"
  oidc_bceid_business_idp_client_id = "fsa-cognito-b-ce-id-business-dev-4090"
  aws_security_group_data = "Data_sg"
  subnet_data_a = "Data_Prod_aza_net"
  subnet_data_b = "Data_Prod_azb_net"
  aws_security_group_app = "App_sg"
  subnet_app_a = "App_Prod_aza_net"
  subnet_app_b = "App_Prod_azb_net"
  front_end_redirect_path = "https://fam.nrs.gov.bc.ca"
  cognito_app_client_logout_chain_url = {
    dev = "${local.common_vars.inputs.idp_logout_chain_dev_url}"
    test = "${local.common_vars.inputs.idp_logout_chain_test_url}"
    prod = "${local.common_vars.inputs.idp_logout_chain_prod_url}"
  }
  fam_callback_urls = [
    "https://fam.nrs.gov.bc.ca/authCallback",
    "https://oidcdebugggersecure-c6af30-dev.apps.gold.devops.gov.bc.ca/"
  ]
  fam_logout_urls = [
    "${local.common_vars.inputs.idp_logout_chain_prod_url}https://fam.nrs.gov.bc.ca",
  ]
  fam_console_idp_name = "PROD-IDIR"
  forest_client_api_base_url = "https://nr-forest-client-api-prod.api.gov.bc.ca/"
  use_override_proxy_endpoints = false
  idim_proxy_api_base_url = "https://nr-fam-idim-lookup-proxy-prod-backend.apps.silver.devops.gov.bc.ca"
EOF
}