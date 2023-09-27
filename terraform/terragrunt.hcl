terraform {
  source = "../..//infrastructure//server"
}

locals {
  region                  = "ca-central-1"

  # !! tfc will be deprecated
  tfc_hostname            = "app.terraform.io"
  tfc_organization        = "bcgov"
  environment             = reverse(split("/", get_terragrunt_dir()))[0]
  tfc_workspace           = get_env("tfc_workspace")  # [AWS_LICENSE_PLATE]-[ENV]

  # Terraform remote config
  tf_remote_state_prefix  = "terraform-remote-state" # Do not change this, given by cloud.pathfinder.
  tf_workspace            = get_env("tf_workspace")  # [AWS_LICENSE_PLATE]-[ENV]
  tf_workspace_component  = "server"
  aws_license_plate       = split("-", "${local.tf_workspace}")[0]
  statefile_bucket_name   = "${local.tf_remote_state_prefix}-${local.tf_workspace}" # Example @tools: "terraform-remote-state-sfha4x-tools"
  statefile_path          = "${local.tf_workspace_component}"
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
    key            = "${local.statefile_path}"            # Path and name of the state file within the bucket
    region         = "${local.region}"                    # AWS region where the bucket is located
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

# TODO, remove next line from pevious role setting.
# role_arn = "arn:aws:iam::$${var.target_aws_account_id}:role/BCGOV_$${var.target_env}_Automation_Admin_Role"
generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite"
  contents  = <<EOF
provider "aws" {
  region  = "${local.region}"
  # assume_role {
  #   role_arn = "$${var.aws_terraform_assume_role}"
  # }
}
EOF
}