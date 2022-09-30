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
    authorize_scopes          = "openid profile email idir"
    client_id                 = var.oidc_idir_dev_idp_client_id
    client_secret             = var.oidc_idir_dev_idp_client_secret
    oidc_issuer               = var.oidc_idir_dev_idp_issuer
    attributes_request_method = "GET"
  }

  attribute_mapping = {
    "custom:idp_name"          = "identity_provider",
    "custom:idp_user_id"       = "idir_user_guid",
    "custom:idp_username"      = "idir_username",
    "custom:idp_display_name"  = "display_name",
    "custom:keycloak_username" = "preferred_username"
  }

}
