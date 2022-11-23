variable "fam_user_pool_name" {
  description = "Name for the FAM user pool"
  type        = string
}

variable "fam_user_pool_domain_name" {
  description = "Name for the FAM user pool domain"
  type        = string
}

variable "famdb_cluster_name" {
  description = "Name for the FAM database cluster -- must be unique"
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

# Variables for IDP setup

variable "oidc_idir_idp_issuer" {
  type = string
}

variable "oidc_idir_idp_client_id" {
  type = string
}

variable "oidc_idir_idp_client_secret" {
  type = string
  sensitive = true
}


variable "oidc_bceid_business_idp_issuer" {
  type = string
}

variable "oidc_bceid_business_idp_client_id" {
  type = string
}

variable "oidc_bceid_business_idp_client_secret" {
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

variable "local_frontend_redirect_path" {
  description = "Path to local FAM front-end (for redirect URI), only for dev"
  type = string
  default = ""
}