include {
  path = find_in_parent_folders()
}

generate "test_tfvars" {
  path              = "test.auto.tfvars"
  if_exists         = "overwrite"
  disable_signature = true
  contents          = <<-EOF
  target_env = "test"
  # cloudfront_vanity_domain = "fam-tst.nrs.gov.bc.ca"
  # cloudfront_certificate_arn = "arn:aws:acm:us-east-1:006519389725:certificate/0c576707-d0fe-4529-bf83-4ee15b5349b7"
EOF
}
