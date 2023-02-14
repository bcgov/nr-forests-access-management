# IDIR IDP that goes to Keycloak and SiteMinder CLP

resource "aws_cognito_identity_provider" "dev_idir_oidc_provider" {
  user_pool_id  = aws_cognito_user_pool.fam_user_pool.id
  provider_name = "DEV-IDIR"
  provider_type = "OIDC"

  provider_details = {
    authorize_scopes          = "openid profile email idir"
    client_id                 = var.oidc_idir_idp_client_id
    client_secret             = var.dev_oidc_idir_idp_client_secret
    oidc_issuer               = var.dev_oidc_idp_issuer
    attributes_request_method = "GET"
  }

  attribute_mapping = {
    email                      = "email",
    "custom:idp_name"          = "identity_provider",
    "custom:idp_user_id"       = "idir_user_guid",
    "custom:idp_username"      = "idir_username",
    "custom:idp_display_name"  = "display_name",
    "custom:keycloak_username" = "preferred_username"
  }
}

resource "aws_cognito_identity_provider" "test_idir_oidc_provider" {
  user_pool_id  = aws_cognito_user_pool.fam_user_pool.id
  provider_name = "TEST-IDIR"
  provider_type = "OIDC"

  provider_details = {
    authorize_scopes          = "openid profile email idir"
    client_id                 = var.oidc_idir_idp_client_id
    client_secret             = var.test_oidc_idir_idp_client_secret
    oidc_issuer               = var.test_oidc_idp_issuer
    attributes_request_method = "GET"
  }

  attribute_mapping = {
    email                      = "email",
    "custom:idp_name"          = "identity_provider",
    "custom:idp_user_id"       = "idir_user_guid",
    "custom:idp_username"      = "idir_username",
    "custom:idp_display_name"  = "display_name",
    "custom:keycloak_username" = "preferred_username"
  }

}

resource "aws_cognito_identity_provider" "prod_idir_oidc_provider" {
  user_pool_id  = aws_cognito_user_pool.fam_user_pool.id
  provider_name = "PROD-IDIR"
  provider_type = "OIDC"

  provider_details = {
    authorize_scopes          = "openid profile email idir"
    client_id                 = var.oidc_idir_idp_client_id
    client_secret             = var.prod_oidc_idir_idp_client_secret
    oidc_issuer               = var.prod_oidc_idp_issuer
    attributes_request_method = "GET"
  }

  attribute_mapping = {
    email                      = "email",
    "custom:idp_name"          = "identity_provider",
    "custom:idp_user_id"       = "idir_user_guid",
    "custom:idp_username"      = "idir_username",
    "custom:idp_display_name"  = "display_name",
    "custom:keycloak_username" = "preferred_username"
  }

}

# Developer notes: we're capturing all the fields from the upstream IDP, but we really don't need them all. Only scope necessary is openid.
# It's more secure to only enable the exact fields that you need so that personal information isn't passed around in tokens unnecessarily

variable "minimum_read_list" {
  description = "The list of required read attributes for all clients"
  type        = list(string)
  default     = ["custom:idp_name", "custom:idp_user_id", "custom:idp_username", "custom:idp_display_name"]
}

variable "minimum_write_list" {
  description = "The list of required write attributes for all clients"
  type        = list(string)
  default     = ["email", "custom:idp_name", "custom:idp_user_id", "custom:idp_username"]
}

variable "all_read_list_idir" {
  description = "The list of all read attributes for IDIR clients"
  type        = list(string)
  default     = ["email", "email_verified", "name", "family_name", "given_name", "preferred_username", "profile", "custom:idp_display_name", "custom:idp_name", "custom:idp_user_id", "custom:idp_username", "custom:keycloak_username"]
}

variable "all_write_list_idir" {
  description = "The list of all write attributes for IDIR clients"
  type        = list(string)
  default     = ["email", "name", "family_name", "given_name", "preferred_username", "profile", "custom:idp_display_name", "custom:idp_name", "custom:idp_user_id", "custom:idp_username", "custom:keycloak_username"]
}