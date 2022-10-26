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
