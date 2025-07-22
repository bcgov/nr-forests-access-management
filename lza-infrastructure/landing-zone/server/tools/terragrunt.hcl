include {
  path = find_in_parent_folders()
}

generate "tools_tfvars" {
  path              = "tools.auto.tfvars"
  if_exists         = "overwrite"
  disable_signature = true
  contents          = <<-EOF
  subnet_data_a = "Data_Tools_aza_net"
  subnet_data_b = "Data_Tools_azb_net"
  subnet_app_a = "App_Tools_aza_net"
  subnet_app_b = "App_Tools_azb_net"
EOF
}