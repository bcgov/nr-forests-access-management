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
  fam_user_pool_name = "tools-fam-user-pool-bcsc"
  fam_user_pool_domain_name = "tools-fam-user-pool-domain"
  famdb_cluster_name = "tools-fam-cluster"
  oidc_idir_idp_client_id = "fsa-cognito-idir-dev-4088"
  oidc_idir_idp_issuer = "https://dev.loginproxy.gov.bc.ca/auth/realms/standard"
  oidc_bceid_business_idp_client_id = "fsa-cognito-b-ce-id-business-dev-4090"
  aws_security_group_data = "Data_sg"
  subnet_data_a = "Data_Tools_aza_net"
  subnet_data_b = "Data_Tools_azb_net"
  aws_security_group_app = "App_sg"
  subnet_app_a = "App_Tools_aza_net"
  subnet_app_b = "App_Tools_azb_net"
  cognito_app_client_logout_chain_url = {
    dev = "${local.common_vars.inputs.idp_logout_chain_dev_url}"
    test = "${local.common_vars.inputs.idp_logout_chain_test_url}"
    prod = "${local.common_vars.inputs.idp_logout_chain_prod_url}"
  }
  front_end_redirect_path = "https://d3d7kmp8kmi5ix.cloudfront.net"
  fam_callback_urls = [
    "https://d3d7kmp8kmi5ix.cloudfront.net/authCallback",
    "http://localhost:5173/authCallback",
    "http://localhost:8000/docs/oauth2-redirect",
    "https://oidcdebuggersecure-3d5c3f-dev.apps.silver.devops.gov.bc.ca/"
  ]
  fam_logout_urls = [
    "${local.common_vars.inputs.idp_logout_chain_dev_url}https://d3d7kmp8kmi5ix.cloudfront.net",
    "${local.common_vars.inputs.idp_logout_chain_dev_url}http://localhost:5173"
  ]
  fam_console_idp_name = "DEV-IDIR"
  forest_client_api_base_url = "https://nr-forest-client-api-test.api.gov.bc.ca"
  use_override_proxy_endpoints = true
  dev_override_bcsc_userinfo_proxy_endpoint = "https://c727z9v3cc.execute-api.ca-central-1.amazonaws.com/v1/bcsc/userinfo/dev"
  test_override_bcsc_userinfo_proxy_endpoint = "https://c727z9v3cc.execute-api.ca-central-1.amazonaws.com/v1/bcsc/userinfo/test"
  prod_override_bcsc_userinfo_proxy_endpoint = "https://c727z9v3cc.execute-api.ca-central-1.amazonaws.com/v1/bcsc/userinfo/prod"
EOF
}
