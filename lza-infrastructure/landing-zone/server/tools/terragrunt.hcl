include {
  path = find_in_parent_folders()
}

locals {
  common_vars = read_terragrunt_config(find_in_parent_folders("common_vars.hcl"))
}

generate "tools_tfvars" {
  path              = "tools.auto.tfvars"
  if_exists         = "overwrite"
  disable_signature = true
  contents          = <<-EOF
  target_env = "tools"
  famdb_cluster_name = "tools-fam-cluster"
  fam_user_pool_name = "lza-tools-fam-user-pool-bcsc"
  fam_user_pool_domain_name = "lza-tools-fam-user-pool-domain"
  oidc_idir_idp_client_id = "fsa-cognito-idir-dev-4088"
  oidc_idir_idp_issuer = "https://dev.loginproxy.gov.bc.ca/auth/realms/standard"
  oidc_bceid_business_idp_client_id = "fsa-cognito-b-ce-id-business-dev-4090"
  subnet_data_a = "Tools-Data-A"
  subnet_data_b = "Tools-Data-B"
  subnet_app_a = "Tools-App-A"
  subnet_app_b = "Tools-App-B"
  subnet_web_a = "Tools-Web-MainTgwAttach-A"
  subnet_web_b = "Tools-Web-MainTgwAttach-B"
  cognito_app_client_logout_chain_url = {
    dev = "${local.common_vars.inputs.idp_logout_chain_dev_url}"
    test = "${local.common_vars.inputs.idp_logout_chain_test_url}"
    prod = "${local.common_vars.inputs.idp_logout_chain_prod_url}"
    tools = "${local.common_vars.inputs.idp_logout_chain_tools_url}"
  }
  # front_end_redirect_path = "https://fam-tools.nrs.gov.bc.ca"
  front_end_redirect_path = "https://d3dndacxwfefe0.cloudfront.net"
  fam_callback_urls = [
    "https://fam-tools.nrs.gov.bc.ca/authCallback",
    "https://d3dndacxwfefe0.cloudfront.net/authCallback"
    "http://localhost:5173/authCallback",
    "http://localhost:8000/docs/oauth2-redirect",
    "http://localhost:8001/docs/oauth2-redirect"
  ]
  fam_logout_urls = [
    "${local.common_vars.inputs.idp_logout_chain_test_url}https://fam-tools.nrs.gov.bc.ca",
    "${local.common_vars.inputs.idp_logout_chain_test_url}https://d3dndacxwfefe0.cloudfront.net",
    "${local.common_vars.inputs.idp_logout_chain_test_url}http://localhost:5173"
  ]
  fam_console_idp_name = "TEST-IDIR"
  fam_console_idp_name_bceid = "TEST-BCEIDBUSINESS"
  forest_client_api_base_url_test = "${local.common_vars.inputs.forest_client_api_test_base_url}"
  use_override_proxy_endpoints = false
EOF
}