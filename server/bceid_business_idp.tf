# IDIR IDP that goes to Keycloak and SiteMinder CLP 


variable "oidc_bceid_business_dev_idp_issuer" {
  type = string
}

variable "oidc_bceid_business_dev_idp_client_id" {
  type = string
}

variable "oidc_bceid_business_dev_idp_client_secret" {
  type = string
}

resource "aws_cognito_identity_provider" "bceid_business_oidc_provider" {
  user_pool_id  = aws_cognito_user_pool.fam_user_pool.id
  provider_name = "BCEIDBUSINESS"
  provider_type = "OIDC"

  provider_details = {
    authorize_scopes          = "openid profile email bceidbusiness"
    client_id                 = var.oidc_bceid_business_dev_idp_client_id
    client_secret             = var.oidc_bceid_business_dev_idp_client_secret
    oidc_issuer               = var.oidc_bceid_business_dev_idp_issuer
    attributes_request_method = "GET"
  }

  attribute_mapping = {
    email                      = "email",
    email_verified             = "email_verified",
    family_name                = "family_name",
    given_name                 = "given_name",
    name                       = "name",
    preferred_username         = "preferred_username",
    username                   = "sub",
    "custom:idp_name"          = "identity_provider",
    "custom:idp_user_id"       = "bceid_user_guid",
    "custom:idp_username"      = "bceid_user_name",
    "custom:idp_display_name"  = "display_name"
    "custom:idp_business_name" = "bceid_business_name",
    "custom:idp_business_id"   = "bceid_business_guid"
  }

}
