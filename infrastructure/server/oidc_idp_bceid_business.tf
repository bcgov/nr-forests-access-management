# BCeID Business IDP that goes to Keycloak and SiteMinder CLP

resource "aws_cognito_identity_provider" "dev_bceid_business_oidc_provider" {
  user_pool_id  = aws_cognito_user_pool.fam_user_pool.id
  provider_name = "DEV-BCEIDBUSINESS"
  provider_type = "OIDC"

  provider_details = {
    authorize_scopes          = "openid profile email bceidbusiness"
    client_id                 = var.oidc_bceid_business_idp_client_id
    client_secret             = var.dev_oidc_bceid_business_idp_client_secret
    oidc_issuer               = var.dev_oidc_idp_issuer
    attributes_request_method = "GET"
    authorize_url             = "${var.dev_oidc_idp_issuer}/protocol/openid-connect/auth"
    token_url                 = "${var.dev_oidc_idp_issuer}/protocol/openid-connect/token"
    attributes_url            = "${var.dev_oidc_idp_issuer}/protocol/openid-connect/userinfo"
    jwks_uri                  = "${var.dev_oidc_idp_issuer}/protocol/openid-connect/certs"
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

resource "aws_cognito_identity_provider" "test_bceid_business_oidc_provider" {
  user_pool_id  = aws_cognito_user_pool.fam_user_pool.id
  provider_name = "TEST-BCEIDBUSINESS"
  provider_type = "OIDC"

  provider_details = {
    authorize_scopes          = "openid profile email bceidbusiness"
    client_id                 = var.oidc_bceid_business_idp_client_id
    client_secret             = var.test_oidc_bceid_business_idp_client_secret
    oidc_issuer               = var.test_oidc_idp_issuer
    attributes_request_method = "GET"
    authorize_url             = "${var.test_oidc_idp_issuer}/protocol/openid-connect/auth"
    token_url                 = "${var.test_oidc_idp_issuer}/protocol/openid-connect/token"
    attributes_url            = "${var.test_oidc_idp_issuer}/protocol/openid-connect/userinfo"
    jwks_uri                  = "${var.test_oidc_idp_issuer}/protocol/openid-connect/certs"
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

# TODO: Production is not provisioned by IDIM.
# Update client_secret and oidc issuer when it is
# Will need to put in the GitHub Secret at that time as well
resource "aws_cognito_identity_provider" "prod_bceid_business_oidc_provider" {
  user_pool_id  = aws_cognito_user_pool.fam_user_pool.id
  provider_name = "PROD-BCEIDBUSINESS"
  provider_type = "OIDC"

  provider_details = {
    authorize_scopes          = "openid profile email bceidbusiness"
    client_id                 = var.oidc_bceid_business_idp_client_id
    client_secret             = var.prod_oidc_bceid_business_idp_client_secret
    oidc_issuer               = var.prod_oidc_idp_issuer
    attributes_request_method = "GET"
    authorize_url             = "${var.prod_oidc_idp_issuer}/protocol/openid-connect/auth"
    token_url                 = "${var.prod_oidc_idp_issuer}/protocol/openid-connect/token"
    attributes_url            = "${var.prod_oidc_idp_issuer}/protocol/openid-connect/userinfo"
    jwks_uri                  = "${var.prod_oidc_idp_issuer}/protocol/openid-connect/certs"
  }

  attribute_mapping = {
    email                      = "email",
    email_verified             = "email_verified",
    "custom:idp_name"          = "identity_provider",
    "custom:idp_user_id"       = "bceid_user_guid",
    "custom:idp_username"      = "bceid_username",
    "custom:idp_display_name"  = "display_name"
    "custom:idp_business_name" = "bceid_business_name",
    "custom:idp_business_id"   = "bceid_business_guid",
    "custom:keycloak_username" = "preferred_username"
  }
}

