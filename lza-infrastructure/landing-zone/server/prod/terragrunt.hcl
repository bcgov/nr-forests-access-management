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
  target_env = "prod"
  fam_user_pool_name = "lza-prod-fam-user-pool-bcsc"
  fam_user_pool_domain_name = "lza-prod-fam-user-pool-domain"
  famdb_cluster_name = "prod-fam-cluster"
  oidc_idir_idp_client_id = "fsa-cognito-idir-dev-4088"
  oidc_idir_idp_issuer = "https://loginproxy.gov.bc.ca/auth/realms/standard"
  oidc_bceid_business_idp_client_id = "fsa-cognito-b-ce-id-business-dev-4090"
  subnet_data_a = "Prod-Data-A"
  subnet_data_b = "Prod-Data-B"
  subnet_app_a = "Prod-App-A"
  subnet_app_b = "Prod-App-B"
  subnet_web_a = "Prod-Web-MainTgwAttach-A"
  subnet_web_b = "Prod-Web-MainTgwAttach-B"
  # front_end_redirect_path = "https://fam.nrs.gov.bc.ca"
  front_end_redirect_path = "https://dfqhrntsb4jgq.cloudfront.net"
  cognito_app_client_logout_chain_url = {
    dev = "${local.common_vars.inputs.idp_logout_chain_dev_url}"
    test = "${local.common_vars.inputs.idp_logout_chain_test_url}"
    prod = "${local.common_vars.inputs.idp_logout_chain_prod_url}"
  }
  fam_callback_urls = [
    "https://fam.nrs.gov.bc.ca/authCallback",
    "https://dfqhrntsb4jgq.cloudfront.net/authCallback"
  ]
  fam_logout_urls = [
    "${local.common_vars.inputs.idp_logout_chain_prod_url}https://fam.nrs.gov.bc.ca",
    "${local.common_vars.inputs.idp_logout_chain_prod_url}https://dfqhrntsb4jgq.cloudfront.net",
  ]
  fam_console_idp_name = "PROD-IDIR"
  fam_console_idp_name_bceid = "PROD-BCEIDBUSINESS"
  forest_client_api_base_url_test = "${local.common_vars.inputs.forest_client_api_test_base_url}"
  forest_client_api_base_url_prod = "${local.common_vars.inputs.forest_client_api_prod_base_url}"
  use_override_proxy_endpoints = false
  idim_proxy_api_base_url_prod = "https://nr-fam-idim-lookup-proxy-prod-backend.apps.silver.devops.gov.bc.ca"
EOF
}
