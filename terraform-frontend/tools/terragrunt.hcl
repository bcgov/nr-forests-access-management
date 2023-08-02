include {
  path = find_in_parent_folders()
}

generate "tools_tfvars" {
  path              = "tools.auto.tfvars"
  if_exists         = "overwrite"
  disable_signature = true
  contents          = <<-EOF
  cloudfront_vanity_domain = ""
  cloudfront_certificate_arn = ""
EOF
}
