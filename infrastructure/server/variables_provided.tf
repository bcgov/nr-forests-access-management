variable "fam_user_pool_name" {
  description = "Name for the FAM user pool"
  type        = string
}

variable "fam_user_pool_domain_name" {
  description = "Name for the FAM user pool domain"
  type        = string
}

variable "famdb_cluster_name" {
  description = "Name for the FAM database cluster"
  type        = string
}


variable "famdb_subnet_group_name" {
  description = "Name for the FAM database subnet group"
  type        = string
}

# Variables for flyway invocation

variable "github_repository" {
  type = string
}

variable "github_branch" {
  type = string
}

variable "github_commit" {
  type = string
}

variable "github_event" {
  type = string
}

# OIDC issuers at Pathfinder SSO (Keycloak)

variable "dev_oidc_idp_issuer" {
  type = string
  default = "https://dev.loginproxy.gov.bc.ca/auth/realms/standard"
}

variable "test_oidc_idp_issuer" {
  type = string
  default = "https://test.loginproxy.gov.bc.ca/auth/realms/standard"
}

variable "prod_oidc_idp_issuer" {
  type = string
  default = "https://loginproxy.gov.bc.ca/auth/realms/standard"
}

# Variables for Pathfinder SSO client ID (same in dev, test, prod)

variable "oidc_idir_idp_client_id" {
  type = string
  default = "fsa-cognito-idir-dev-4088"
}

variable "oidc_bceid_business_idp_client_id" {
  type = string
  default = "fsa-cognito-b-ce-id-business-dev-4090"
}

# Client secrets for IDIR and BCeID in each environment

variable "dev_oidc_idir_idp_client_secret" {
  type = string
  sensitive = true
}

variable "test_oidc_idir_idp_client_secret" {
  type = string
  sensitive = true
}

variable "prod_oidc_idir_idp_client_secret" {
  type = string
  sensitive = true
}

variable "dev_oidc_bceid_business_idp_client_secret" {
  type = string
  sensitive = true
}

variable "test_oidc_bceid_business_idp_client_secret" {
  type = string
  sensitive = true
}

variable "prod_oidc_bceid_business_idp_client_secret" {
  type = string
  sensitive = true
}

# Networking Variables

variable "aws_security_group_data" {
  description = "Value of the name tag for the DATA security group"
  type = string
}

variable "subnet_data_a" {
  description = "Value of the name tag for a subnet in the DATA security group"
  type = string
}

variable "subnet_data_b" {
  description = "Value of the name tag for a subnet in the DATA security group"
  type = string
}

variable "aws_security_group_app" {
  description = "Value of the name tag for the APP security group"
  type = string
}

variable "subnet_app_a" {
  description = "Value of the name tag for a subnet in the APP security group"
  type = string
}

variable "subnet_app_b" {
  description = "Value of the name tag for a subnet in the APP security group"
  type = string
}

# Variables to control flyway process

variable "execute_flyway" {
  description = "Toggle for whether to execute flyway (suppress on terraform plan)"
  type = bool
  default = false
}

variable "db_cluster_snapshot_identifier" {
  description = "Value fo the db_cluster_snapshot_identifier used for the fam_pre_flyway_snapshot resource (flyway.tf).  Validation will identify length constraint violations before it attempts to deploy"
  validation {
    condition     = length(var.db_cluster_snapshot_identifier) < 63
    error_message = "The aws_db_cluster_snapshot property db_cluster_snapshot_identifier cannot exceed 63 characters."
  }
}

# Variables for front-end config

variable "front_end_redirect_path" {
  description = "Path to public FAM front-end (for redirect URI)"
  type = string
}

variable "api_gateway_stage_name" {
  description = "Stage name for the REST API in API Gateway (appears in URI)"
  type = string
  default = "v1"
}

variable "fam_console_idp_name" {
  description = "Identifies which version of IDIR to use (DEV, TEST, or PROD)"
  type = string
}

