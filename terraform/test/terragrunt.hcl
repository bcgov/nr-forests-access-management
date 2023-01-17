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
  front_end_redirect_path = "https://d14evo4qtbdgsm.cloudfront.net"
  fam_console_idp_name = "TEST-IDIR"
EOF
}