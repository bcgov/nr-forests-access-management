terraform {
  source = "../..//infrastructure//server"
}

locals {
  tfc_hostname     = "app.terraform.io"
  tfc_organization = "bcgov"
  tfc_workspace    = get_env("TFC-WORKSPACE")
  environment      = reverse(split("/", get_terragrunt_dir()))[0]
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
github_repository = "https://github.com/${{ github.repository }}"
github_branch = "${{ github.ref_name }}"
github_commit = "${{ github.sha }}"
github_event = "${{ github.event_name }}"
oidc_idir_dev_idp_client_id = "${{ secrets.OIDC_IDIR_DEV_IDP_CLIENT_ID }}"
oidc_idir_dev_idp_client_secret = "${{ secrets.OIDC_IDIR_DEV_IDP_CLIENT_SECRET }}"
oidc_idir_dev_idp_issuer = "${{ secrets.OIDC_IDIR_DEV_IDP_ISSUER }}"
oidc_bceid_business_dev_idp_client_id = "${{ secrets.OIDC_BCEID_BUSINESS_DEV_IDP_CLIENT_ID }}"
oidc_bceid_business_dev_idp_client_secret = "${{ secrets.OIDC_BCEID_BUSINESS_DEV_IDP_CLIENT_SECRET }}"
oidc_bceid_business_dev_idp_issuer = "${{ secrets.OIDC_BCEID_BUSINESS_DEV_IDP_ISSUER }}"
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