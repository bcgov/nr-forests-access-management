include {
  path = find_in_parent_folders()
}

generate "prod_tfvars" {
  path              = "prod.auto.tfvars"
  if_exists         = "overwrite"
  disable_signature = true
  contents          = <<-EOF
  fam_user_pool_name = "prod-fam-user-pool"
  fam_user_pool_domain_name = "prod-fam-user-pool-domain"
  famdb_cluster_name = "prod-fam-cluster-restore"
  oidc_idir_idp_client_id = "fsa-cognito-idir-dev-4088"
  oidc_idir_idp_issuer = "https://loginproxy.gov.bc.ca/auth/realms/standard"
  oidc_bceid_business_idp_client_id = "fsa-cognito-b-ce-id-business-dev-4090"
  oidc_bceid_business_idp_issuer = "https://loginproxy.gov.bc.ca/auth/realms/standard"
  aws_security_group_data = "Data_sg"
  subnet_data_a = "Data_Prod_aza_net"
  subnet_data_b = "Data_Prod_azb_net"
  aws_security_group_app = "App_sg"
  subnet_app_a = "App_Prod_aza_net"
  subnet_app_b = "App_Prod_azb_net"
  front_end_redirect_path = "https://fam.nrs.gov.bc.ca"
  local_frontend_redirect_path = "http://localhost:5173"
  fam_console_idp_name = "PROD-IDIR"
EOF
}