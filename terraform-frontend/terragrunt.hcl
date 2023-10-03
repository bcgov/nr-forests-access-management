terraform {
  source = "../..//infrastructure//frontend"
}

locals {
  # !! tfc will be deprecated
  # tfc_hostname     = "app.terraform.io"
  # tfc_organization = "bcgov"
  # environment      = reverse(split("/", get_terragrunt_dir()))[0]
  # tfc_workspace    = get_env("tfc_workspace")

  # Terraform remote S3 config
  tf_remote_state_prefix  = "terraform-remote-state" # Do not change this, given by cloud.pathfinder.
  aws_license_plate       = get_env("licenceplate")
  target_env              = get_env("target_env")
  statefile_bucket_name   = "${local.tf_remote_state_prefix}-${local.aws_license_plate}-${local.target_env}" # Example @tools: "terraform-remote-state-sfha4x-tools"
  statefile_key          = "frontend.tfstate"
  statelock_table_name    = "${local.tf_remote_state_prefix}-lock-${local.aws_license_plate}" # Example @tools: "terraform-remote-state-lock-sfha4x"
}

# generate "remote_state" {
#   path      = "backend.tf"
#   if_exists = "overwrite"
#   contents  = <<EOF
# terraform {
#   backend "remote" {
#     hostname = "${local.tfc_hostname}"
#     organization = "${local.tfc_organization}"
#     workspaces {
#       name = "${local.tfc_workspace}"
#     }
#   }
# }
# EOF
# }

# Migratoin from TFC to S3
generate "remote_state" {
  path      = "backend.tf"
  if_exists = "overwrite"
  contents  = <<EOF
terraform {
  backend "s3" {
    bucket         = "${local.statefile_bucket_name}"
    key            = "${local.statefile_key}"            # Path and name of the state file within the bucket
    region         = "ca-central-1"                       # AWS region where the bucket is located
    dynamodb_table = "${local.statelock_table_name}"
    encrypt        = true
  }
}
EOF
}

generate "tfvars" {
  path              = "terragrunt.auto.tfvars"
  if_exists         = "overwrite"
  disable_signature = true
  contents          = <<-EOF
EOF
}

generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite"
  contents  = <<EOF
provider "aws" {
  region  = "ca-central-1"
}

# Additional provider configuration for us-east-1 region; resources can reference this as `aws.east`.
# This is essential for adding WAF ACL rules as they are only available at us-east-1.
# See AWS doc: https://docs.aws.amazon.com/pdfs/waf/latest/developerguide/waf-dg.pdf#how-aws-waf-works-resources
#     on section: "Amazon CloudFront distributions"
# Also refer to ticket (https://app.zenhub.com/workspaces/fsa-fingerprint-61f04f08304d3e001a4f2578/issues/gh/bcgov/nr-forests-access-management/725)
#     for specific error ("CLOUDFRONT" is not valid)
provider "aws" {
  alias  = "east"
  region = "us-east-1"
}

EOF
}