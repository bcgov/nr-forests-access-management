include {
  path = find_in_parent_folders()
}

generate "test_tfvars" {
  path              = "test.auto.tfvars"
  if_exists         = "overwrite"
  disable_signature = true
  contents          = <<-EOF
  fam_user_pool_name = "prod-fam-user-pool"
  fam_user_pool_domain_name = "prod-fam-user-pool-domain"
  famdb_cluster_name = "prod-fam-cluster"
EOF
}