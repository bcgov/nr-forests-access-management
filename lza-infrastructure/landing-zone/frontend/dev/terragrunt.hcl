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
  # cloudfront_certificate_arn = "arn:aws:acm:us-east-1:111009054567:certificate/86c30b80-cb3a-46d1-a829-1cfff885b302"
EOF
}
