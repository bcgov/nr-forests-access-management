include {
  path = find_in_parent_folders()
}

generate "tools_tfvars" {
  path              = "tools.auto.tfvars"
  if_exists         = "overwrite"
  disable_signature = true
  contents          = <<-EOF
  target_env = "tools"
  # cloudfront_vanity_domain = "fam-tools.nrs.gov.bc.ca"
  # cloudfront_certificate_arn = "arn:aws:acm:us-east-1:377481750915:certificate/1c653a26-ad35-4e00-8c1b-3c159948d09f"
EOF
}
