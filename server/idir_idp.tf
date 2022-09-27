# IDIR IDP that goes to Keycloak and SiteMinder CLP 


variable "oidc_idir_dev_idp_issuer" {
  type = string
}

variable "oidc_idir_dev_idp_client_id" {
  type = string
}

variable "oidc_idir_dev_idp_client_secret" {
  type = string
}

resource "aws_cognito_identity_provider" "idir_oidc_provider" {
  user_pool_id  = aws_cognito_user_pool.fam_user_pool.id
  provider_name = "IDIR"
  provider_type = "OIDC"

  provider_details = {
    authorize_scopes = "openid profile email"
    client_id        = var.oidc_idir_dev_idp_client_id
    client_secret    = var.oidc_idir_dev_idp_client_secret
    oidc_issuer      = var.oidc_idir_dev_idp_issuer
    attributes_request_method = "GET"
  }

  attribute_mapping = {
    email                      = "email",
    email_verified             = "sub",
    family_name                = "family_name",
    given_name                 = "given_name",
    name                       = "name",
    preferred_username         = "preferred_username",
    username                   = "sub",
    "custom:display_name"      = "display_name",
    "custom:identity_provider" = "identity_provider",
    "custom:user_guid"         = "idir_user_guid"
  }

}
