include {
  path = find_in_parent_folders()
}

generate "test_tfvars" {
  path              = "test.auto.tfvars"
  if_exists         = "overwrite"
  disable_signature = true
  contents          = <<-EOF
  target_env = "test"
  cloudfront_vanity_domain = "fam-tst.nrs.gov.bc.ca"
  cloudfront_certificate_arn = "arn:aws:acm:us-east-1:267670768149:certificate/fd89695a-7026-4ebf-befa-b386a26b2382"
EOF
}
