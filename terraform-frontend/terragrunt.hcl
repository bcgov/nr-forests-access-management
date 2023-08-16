terraform {
  source = "../..//infrastructure//frontend"
}

locals {
  tfc_hostname     = "app.terraform.io"
  tfc_organization = "bcgov"
  environment      = reverse(split("/", get_terragrunt_dir()))[0]
  tfc_workspace    = get_env("tfc_workspace")
}

generate "remote_state" {
  path      = "backend.tf"
  if_exists = "overwrite"
  contents  = <<EOF
terraform {
  backend "remote" {
    hostname = "${local.tfc_hostname}"
    organization = "${local.tfc_organization}"
    workspaces {
      name = "${local.tfc_workspace}"
    }
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
  assume_role {
    role_arn = "arn:aws:iam::$${var.target_aws_account_id}:role/BCGOV_$${var.target_env}_Automation_Admin_Role"
  }
 default_tags {
    tags = {
      managed-by = "terraform"
    }
  }

}
EOF
}