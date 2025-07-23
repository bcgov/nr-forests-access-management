include {
  path = find_in_parent_folders()
}

generate "tools_tfvars" {
  path              = "tools.auto.tfvars"
  if_exists         = "overwrite"
  disable_signature = true
  contents          = <<-EOF
  target_env = "tools"
  subnet_data_a = "Tools-Data-A"
  subnet_data_b = "Tools-Data-B"
  subnet_app_a = "Tools-App-A"
  subnet_app_b = "Tools-App-B"
  subnet_web_a = "Tools-Web-MainTgwAttach-A"
  subnet_web_b = "Tools-Web-MainTgwAttach-B"
EOF
}