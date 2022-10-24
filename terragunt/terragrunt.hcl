terraform {
  source = "../cognito"
}

# Indicate what region to deploy the resources into
generate "provider" {
  path = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents = <<EOF
provider "aws" {
  region = "ca-central-1"
  assume_role {
    role_arn = "arn:aws:iam::${var.target_aws_account_id}:role/BCGOV_${var.target_env}_Automation_Admin_Role"
  }
}
EOF
}

# Indicate the input values to use for the variables of the module.
inputs = {
  fam_user_pool_name = "fam-user-pool"
  fam_user_pool_domain_name = "test-fam-user-pool-domain"
}

