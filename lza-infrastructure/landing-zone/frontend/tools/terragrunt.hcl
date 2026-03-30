include {
  path = find_in_parent_folders()
}

generate "tools_tfvars" {
  path              = "tools.auto.tfvars"
  if_exists         = "overwrite"
  disable_signature = true
  contents          = <<-EOF
  target_env = "tools"
  cloudfront_vanity_domain = "fam-tools.nrs.gov.bc.ca"
  cloudfront_certificate_arn = "arn:aws:acm:us-east-1:596387592149:certificate/3c67cb7c-a7db-4a1d-aaeb-9a6bc18b4395"
EOF
}
