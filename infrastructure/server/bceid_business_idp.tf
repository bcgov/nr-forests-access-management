# IDIR IDP that goes to Keycloak and SiteMinder CLP 

resource "aws_cognito_identity_provider" "bceid_business_oidc_provider" {
  user_pool_id  = aws_cognito_user_pool.fam_user_pool.id
  provider_name = "BCEIDBUSINESS"
  provider_type = "OIDC"

  provider_details = {
    authorize_scopes          = "openid profile email bceidbusiness"
    client_id                 = var.oidc_bceid_business_idp_client_id
    client_secret             = var.oidc_bceid_business_idp_client_secret
    oidc_issuer               = var.oidc_bceid_business_idp_issuer
    attributes_request_method = "GET"
  }

  attribute_mapping = {
    email                      = "email",
    "custom:idp_name"          = "identity_provider",
    "custom:idp_user_id"       = "bceid_user_guid",
    "custom:idp_username"      = "bceid_username",
    "custom:idp_display_name"  = "display_name"
    "custom:idp_business_name" = "bceid_business_name",
    "custom:idp_business_id"   = "bceid_business_guid",
    "custom:keycloak_username" = "preferred_username"
  }

}
