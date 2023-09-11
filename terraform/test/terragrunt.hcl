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
  fam_user_pool_name = "test-fam-user-pool-bcsc"
  fam_user_pool_domain_name = "test-fam-user-pool-domain"
  famdb_cluster_name = "test-fam-cluster"
  aws_security_group_data = "fam_data_sg"
  subnet_data_a = "Data_Test_aza_net"
  subnet_data_b = "Data_Test_azb_net"
  aws_security_group_app = "fam_app_sg"
  subnet_app_a = "App_Test_aza_net"
  subnet_app_b = "App_Test_azb_net"
  cognito_app_client_logout_chain_url = {
    dev = "${local.common_vars.inputs.idp_logout_chain_dev_url}"
    test = "${local.common_vars.inputs.idp_logout_chain_test_url}"
    prod = "${local.common_vars.inputs.idp_logout_chain_prod_url}"
  }
  front_end_redirect_path = "https://fam-tst.nrs.gov.bc.ca"
  fam_callback_urls = [
    "https://fam-tst.nrs.gov.bc.ca/authCallback",
    "http://localhost:5173/authCallback",
    "http://localhost:8000/docs/oauth2-redirect",
    "https://oidcdebugggersecure-c6af30-dev.apps.gold.devops.gov.bc.ca/"
  ]
  fam_logout_urls = [
    "${local.common_vars.inputs.idp_logout_chain_test_url}https://fam-tst.nrs.gov.bc.ca",
    "${local.common_vars.inputs.idp_logout_chain_test_url}http://localhost:5173"
  ]
  fam_console_idp_name = "TEST-IDIR"
  forest_client_api_base_url = "https://nr-forest-client-api-test.api.gov.bc.ca"
  use_override_proxy_endpoints = false
  idim_proxy_api_base_url = "https://nr-fam-idim-lookup-proxy-test-backend.apps.silver.devops.gov.bc.ca"
EOF
}