include {
  path = find_in_parent_folders()
}

locals {
  common_vars = read_terragrunt_config(find_in_parent_folders("common_vars.hcl"))
}

generate "test_tfvars" {
  path              = "test.auto.tfvars"
  if_exists         = "overwrite"
  disable_signature = true
  contents          = <<-EOF
  target_env = "test"
  fam_user_pool_name = "lza-test-fam-user-pool-bcsc"
  fam_user_pool_domain_name = "lza-test-fam-user-pool-domain"
  famdb_cluster_name = "test-fam-cluster"
  subnet_data_a = "Test-Data-A"
  subnet_data_b = "Test-Data-B"
  subnet_app_a = "Test-App-A"
  subnet_app_b = "Test-App-B"
  subnet_web_a = "Test-Web-MainTgwAttach-A"
  subnet_web_b = "Test-Web-MainTgwAttach-B"
  cognito_app_client_logout_chain_url = {
    dev = "${local.common_vars.inputs.idp_logout_chain_dev_url}"
    test = "${local.common_vars.inputs.idp_logout_chain_test_url}"
    prod = "${local.common_vars.inputs.idp_logout_chain_prod_url}"
  }
  # front_end_redirect_path = "https://fam-tst.nrs.gov.bc.ca"
  front_end_redirect_path = "https://dmrxf04cbntge.cloudfront.net"
  fam_callback_urls = [
    "https://fam-tst.nrs.gov.bc.ca/authCallback",
    "https://dmrxf04cbntge.cloudfront.net/authCallback",
    "http://localhost:5173/authCallback",
    "http://localhost:8000/docs/oauth2-redirect",
    "http://localhost:8001/docs/oauth2-redirect"
  ]
  fam_logout_urls = [
    "${local.common_vars.inputs.idp_logout_chain_test_url}https://fam-tst.nrs.gov.bc.ca",
    "${local.common_vars.inputs.idp_logout_chain_test_url}https://dmrxf04cbntge.cloudfront.net",
    "${local.common_vars.inputs.idp_logout_chain_test_url}http://localhost:5173"
  ]
  fam_console_idp_name = "TEST-IDIR"
  fam_console_idp_name_bceid = "TEST-BCEIDBUSINESS"
  forest_client_api_base_url_test = "${local.common_vars.inputs.forest_client_api_test_base_url}"
  use_override_proxy_endpoints = false
EOF
}
