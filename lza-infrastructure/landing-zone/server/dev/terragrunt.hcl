include {
  path = find_in_parent_folders()
}

locals {
  common_vars = read_terragrunt_config(find_in_parent_folders("common_vars.hcl"))
}

generate "dev_tfvars" {
  path              = "dev.auto.tfvars"
  if_exists         = "overwrite"
  disable_signature = true
  contents          = <<-EOF
  target_env = "dev"
  fam_user_pool_name = "dev-fam-user-pool-bcsc"
  fam_user_pool_domain_name = "dev-fam-user-pool-domain"
  famdb_cluster_name = "dev-fam-cluster"
  oidc_idir_idp_client_id = "fsa-cognito-idir-dev-4088"
  oidc_idir_idp_issuer = "https://dev.loginproxy.gov.bc.ca/auth/realms/standard"
  oidc_bceid_business_idp_client_id = "fsa-cognito-b-ce-id-business-dev-4090"
  subnet_data_a = "Dev-Data-A"
  subnet_data_b = "Dev-Data-B"
  subnet_app_a = "Dev-App-A"
  subnet_app_b = "Dev-App-B"
  subnet_web_a = "Dev-Web-MainTgwAttach-A"
  subnet_web_b = "Dev-Web-MainTgwAttach-B"
  cognito_app_client_logout_chain_url = {
    dev = "${local.common_vars.inputs.idp_logout_chain_dev_url}"
    test = "${local.common_vars.inputs.idp_logout_chain_test_url}"
    prod = "${local.common_vars.inputs.idp_logout_chain_prod_url}"
  }

  # front_end_redirect_path = "https://fam-dev.nrs.gov.bc.ca"

  # Use default AWS default temporarily (only known after frotend deployed).
  # Do this for 'front_end_redirect_path', 'fam_callback_urls' and 'fam_logout_urls'
  # Remove later.
  front_end_redirect_path = "https://add-aws-default-temporarily.cloudfront.net"
  fam_callback_urls = [
    "https://fam-dev.nrs.gov.bc.ca/authCallback",
    "http://localhost:5173/authCallback",
    "http://localhost:8000/docs/oauth2-redirect",
    "http://localhost:8001/docs/oauth2-redirect"
  ]
  fam_logout_urls = [
    "${local.common_vars.inputs.idp_logout_chain_test_url}https://fam-dev.nrs.gov.bc.ca",
    "${local.common_vars.inputs.idp_logout_chain_test_url}http://localhost:5173"
  ]
  fam_console_idp_name = "TEST-IDIR"
  fam_console_idp_name_bceid = "TEST-BCEIDBUSINESS"
  forest_client_api_base_url_test = "${local.common_vars.inputs.forest_client_api_test_base_url}"
  use_override_proxy_endpoints = false
  # use_override_proxy_endpoints = true
  # dev_override_bcsc_userinfo_proxy_endpoint = "https://xy7pk81p4h.execute-api.ca-central-1.amazonaws.com/v1/bcsc/userinfo/dev"
  # test_override_bcsc_userinfo_proxy_endpoint = "https://6mud7781pe.execute-api.ca-central-1.amazonaws.com/v1/bcsc/userinfo/test"
  # prod_override_bcsc_userinfo_proxy_endpoint = "https://6mud7781pe.execute-api.ca-central-1.amazonaws.com/v1/bcsc/userinfo/prod"
  # dev_override_bcsc_token_proxy_endpoint = "https://xy7pk81p4h.execute-api.ca-central-1.amazonaws.com/v1/bcsc/token/dev"
  # test_override_bcsc_token_proxy_endpoint = "https://6mud7781pe.execute-api.ca-central-1.amazonaws.com/v1/bcsc/token/test"
  # prod_override_bcsc_token_proxy_endpoint = "https://6mud7781pe.execute-api.ca-central-1.amazonaws.com/v1/bcsc/token/prod"
EOF
}
