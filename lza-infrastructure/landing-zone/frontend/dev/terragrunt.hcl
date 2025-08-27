include {
  path = find_in_parent_folders()
}

generate "dev_tfvars" {
  path              = "dev.auto.tfvars"
  if_exists         = "overwrite"
  disable_signature = true
  contents          = <<-EOF
  target_env = "dev"
  # cloudfront_vanity_domain = "fam-dev.nrs.gov.bc.ca"
  # cloudfront_certificate_arn = "arn:aws:acm:us-east-1:521834415778:certificate/f6ad099b-525e-47e9-8c0b-6c11c5875d08"
EOF
}
