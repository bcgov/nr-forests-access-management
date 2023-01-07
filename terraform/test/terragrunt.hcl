include {
  path = find_in_parent_folders()
}

generate "test_tfvars" {
  path              = "test.auto.tfvars"
  if_exists         = "overwrite"
  disable_signature = true
  contents          = <<-EOF
  fam_user_pool_name = "test-fam-user-pool"
  fam_user_pool_domain_name = "test-fam-user-pool-domain"
  famdb_cluster_name = "test-fam-cluster"
  oidc_idir_idp_client_id = "fsa-cognito-idir-dev-4088"
  oidc_idir_idp_issuer = "https://test.loginproxy.gov.bc.ca/auth/realms/standard"
  oidc_bceid_business_idp_client_id = "fsa-cognito-b-ce-id-business-dev-4090"
  oidc_bceid_business_idp_issuer = "https://test.loginproxy.gov.bc.ca/auth/realms/standard"
  aws_security_group_data = "Data_sg"
  subnet_data_a = "Data_Test_aza_net"
  subnet_data_b = "Data_Test_azb_net"
  aws_security_group_app = "App_sg"
  subnet_app_a = "App_Test_aza_net"
  subnet_app_b = "App_Test_azb_net"
  front_end_redirect_path = "https://d14evo4qtbdgsm.cloudfront.net"
  fam_console_callback_urls = [
    "${var.front_end_redirect_path}/authCallback",
    "${var.fam_api_base_url}/docs/oauth2-redirect",
    "http://localhost:5173/authCallback",
    "http://localhost:8000/docs/oauth2-redirect",
    "https://oidcdebuggersecure-3d5c3f-dev.apps.silver.devops.gov.bc.ca/"
  ]
  fam_console_logout_urls = [
    "${var.front_end_redirect_path}/authLogout",
    "http://localhost:5173/authLogout"
  ]
EOF
}