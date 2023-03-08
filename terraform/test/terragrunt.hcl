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
  aws_security_group_data = "Data_sg"
  subnet_data_a = "Data_Test_aza_net"
  subnet_data_b = "Data_Test_azb_net"
  aws_security_group_app = "App_sg"
  subnet_app_a = "App_Test_aza_net"
  subnet_app_b = "App_Test_azb_net"
  frontend_logout_chain_url = "https://logontest7.gov.bc.ca/clp-cgi/logoff.cgi?retnow=1&returl=https://test.loginproxy.gov.bc.ca/auth/realms/standard/protocol/openid-connect/logout?redirect_uri="
  front_end_redirect_path = "https://fam-tst.nrs.gov.bc.ca"
  fam_callback_urls = [
    "https://fam-tst.nrs.gov.bc.ca/authCallback",
    "${aws_api_gateway_deployment.fam_api_gateway_deployment.invoke_url}/docs/oauth2-redirect",
    "http://localhost:5173/authCallback",
    "http://localhost:8000/docs/oauth2-redirect",
    "https://oidcdebuggersecure-3d5c3f-dev.apps.silver.devops.gov.bc.ca/"
  ]
  fam_logout_urls = [
    "https://logontest7.gov.bc.ca/clp-cgi/logoff.cgi?retnow=1&returl=https://dev.loginproxy.gov.bc.ca/auth/realms/standard/protocol/openid-connect/logout?redirect_uri=https://fam-tst.nrs.gov.bc.ca",
    "https://logontest7.gov.bc.ca/clp-cgi/logoff.cgi?retnow=1&returl=https://dev.loginproxy.gov.bc.ca/auth/realms/standard/protocol/openid-connect/logout?redirect_uri=http://localhost:5173"
  ]
  fam_console_idp_name = "TEST-IDIR"
EOF
}