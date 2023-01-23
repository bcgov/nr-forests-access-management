include {
  path = find_in_parent_folders()
}

generate "dev_tfvars" {
  path              = "dev.auto.tfvars"
  if_exists         = "overwrite"
  disable_signature = true
  contents          = <<-EOF
  cloudfront_vanity_domain = "fam-dev.nrs.gov.bc.ca"
  cloudfront_certificate_arn = "arn:aws:acm:us-east-1:521834415778:certificate/d9407a0e-98b4-47d0-be73-adefe7011d34"
EOF
}
