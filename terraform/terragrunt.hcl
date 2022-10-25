terraform {
  source = "../..//infrastructure//server"
}

locals {
  tfc_hostname     = "app.terraform.io"
  tfc_organization = "bcgov"
  tfc_workspace    = get_env("TFC-WORKSPACE")
  environment      = reverse(split("/", get_terragrunt_dir()))[0]
  github_repository = get_env("github_repository")
  github_branch = get_env("github_branch")
  github_commit = get_env("github_commit")
  github_event = get_env("github_event")
  oidc_idir_idp_client_secret = get_env("oidc_idir_idp_client_secret")
  oidc_bceid_business_idp_client_secret = get_env("oidc_bceid_business_idp_client_secret")
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
github_repository = "${local.github_repository}"
github_branch = "${local.github_branch}"
github_commit = "${local.github_commit}"
github_event = "${local.github_event}"
oidc_idir_dev_idp_client_secret = "${local.oidc_idir_idp_client_secret}"
oidc_bceid_business_dev_idp_client_secret = "${local.oidc_bceid_business_idp_client_secret}"
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
}
EOF
}