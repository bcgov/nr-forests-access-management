include {
  path = find_in_parent_folders()
}

generate "prod_tfvars" {
  path              = "prod.auto.tfvars"
  if_exists         = "overwrite"
  disable_signature = true
  contents          = <<-EOF
  target_env = "prod"
  cloudfront_vanity_domain = "fam.nrs.gov.bc.ca"
  cloudfront_certificate_arn = "arn:aws:acm:us-east-1:068169410803:certificate/43c13e98-65cb-41e9-a709-297dd918785d"
EOF
}
