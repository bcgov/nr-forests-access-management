include {
  path = find_in_parent_folders()
}

generate "prod_tfvars" {
  path              = "prod.auto.tfvars"
  if_exists         = "overwrite"
  disable_signature = true
  contents          = <<-EOF
  cloudfront_vanity_domain = "fam.nrs.gov.bc.ca"
  cloudfront_certificate_arn = "arn:aws:acm:us-east-1:068169410803:certificate/9c1dc7a8-3d95-4ae9-9b65-5deeab780ebe"
EOF
}
