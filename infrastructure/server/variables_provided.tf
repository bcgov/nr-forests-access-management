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

# OIDC issuers at BCSC

variable "dev_bcsc_oidc_idp_issuer" {
  type = string
  default = "https://idtest.gov.bc.ca/oauth2"
}

variable "test_bcsc_oidc_idp_issuer" {
  type = string
  default = "https://idtest.gov.bc.ca/oauth2"
}

variable "prod_bcsc_oidc_idp_issuer" {
  type = string
  default = "https://id.gov.bc.ca/oauth2"
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

# Client secrets for IDIR in each environment

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

# Client secrets for BCeID in each environment

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

# Client secrets for BCSC in each environment

variable "dev_oidc_bcsc_idp_client_secret" {
  type = string
  sensitive = true
}

variable "test_oidc_bcsc_idp_client_secret" {
  type = string
  sensitive = true
}

variable "prod_oidc_bcsc_idp_client_secret" {
  type = string
  sensitive = true
}

# Client IDs for BCSC in each environment

variable "dev_oidc_bcsc_idp_client_id" {
  type = string
  default = "ca.bc.gov.flnr.fam.dev"
}

variable "test_oidc_bcsc_idp_client_id" {
  type = string
  default = "ca.bc.gov.flnr.fam.test"
}

variable "prod_oidc_bcsc_idp_client_id" {
  type = string
  default = "not.yet.implemented"
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

# Integration - API Keys/Secrets
variable "forest_client_api_api_key" {
  type = string
  sensitive = true
}

variable "forest_client_api_base_url" {
  type = string
  sensitive = true
}

variable "idim_proxy_api_base_url" {
  type = string
  sensitive = true
}

variable "idim_proxy_api_api_key" {
  type = string
  sensitive = true
}


# Variables for Cognito Client config

variable "cognito_app_client_logout_chain_url" {
  description = "Url of Siteminder and Keycloak logout chain for Cognito client on all environments(dev, test, prod)"
  type = map
}


# Variables for FAM front-end config

variable "frontend_logout_chain_url" {
  description = "Url of Siteminder and Keycloak logout chain for frontend"
  type = string
  default = "https://logontest7.gov.bc.ca/clp-cgi/logoff.cgi?retnow=1&returl=https://dev.loginproxy.gov.bc.ca/auth/realms/standard/protocol/openid-connect/logout?redirect_uri="
}

variable "front_end_redirect_path" {
  description = "Path to public FAM front-end (for redirect URI)"
  type = string
}

variable "api_gateway_stage_name" {
  description = "Stage name for the REST API in API Gateway (appears in URI)"
  type = string
  default = "v1"
}

variable "fam_callback_urls" {
  description = "Callback urls for Cognito login redirect for FAM"
  type = list
}

variable "fam_logout_urls" {
  description = "Log urls for Cognito logout redirect for FAM"
  type = list
}

variable "fam_console_idp_name" {
  description = "Identifies which version of IDIR to use (DEV, TEST, or PROD)"
  type = string
}

variable "minimum_oidc_attribute_list" {
  description = "Required fields for FAM clients to be able to read and write"
  type        = list(string)
  default     = ["custom:idp_name", "custom:idp_user_id", "custom:idp_username"]
}

variable "maximum_oidc_attribute_read_list" {
  description = "All fields for FAM clients to possibly read"
  type        = list(string)
  default = [
    "address",
    "birthdate",
    "custom:given_names",
    "custom:idp_business_id",
    "custom:idp_business_name",
    "custom:idp_display_name",
    "custom:idp_name",
    "custom:idp_user_id",
    "custom:idp_username",
    "custom:keycloak_username",
    "email", "email_verified",
    "family_name",
    "gender",
    "given_name",
    "locale",
    "middle_name",
    "name",
    "nickname",
    "phone_number",
    "phone_number_verified",
    "picture",
    "preferred_username",
    "profile",
    "updated_at",
    "website",
    "zoneinfo"
  ]

}

variable "maximum_oidc_attribute_write_list" {
  description = "All fields for FAM clients to possibly write"
  type        = list(string)
  default = [
    "address",
    "birthdate",
    "custom:given_names",
    "custom:idp_business_id",
    "custom:idp_business_name",
    "custom:idp_display_name",
    "custom:idp_name",
    "custom:idp_user_id",
    "custom:idp_username",
    "custom:keycloak_username",
    "email",
    "family_name",
    "gender",
    "given_name",
    "locale",
    "middle_name",
    "name",
    "nickname",
    "phone_number",
    "picture",
    "preferred_username",
    "profile",
    "updated_at",
    "website",
    "zoneinfo"]
}

# Variables for connecting Cognito to BCSC OIDC

variable "use_override_proxy_endpoints" {
  description = "Toggle for whether to execute flyway (suppress on terraform plan)"
  type = bool
  default = false
}

variable "dev_override_bcsc_userinfo_proxy_endpoint" {
  description = "Endpoint for Cognito to get userinfo data for BCSC DEV environment"
  type = string
  default = "not used unless overridden in terragrunt"
}

variable "test_override_bcsc_userinfo_proxy_endpoint" {
  description = "Endpoint for Cognito to get userinfo data for BCSC TEST environment"
  type = string
  default = "not used unless overridden in terragrunt"
}

variable "prod_override_bcsc_userinfo_proxy_endpoint" {
  description = "Endpoint for Cognito to get userinfo data for BCSC PROD environment"
  type = string
  default = "not used unless overridden in terragrunt"
}