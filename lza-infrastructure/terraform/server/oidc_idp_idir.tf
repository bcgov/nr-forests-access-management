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
    authorize_url             = "${var.dev_oidc_idp_issuer}/protocol/openid-connect/auth"
    token_url                 = "${var.dev_oidc_idp_issuer}/protocol/openid-connect/token"
    attributes_url            = "${var.dev_oidc_idp_issuer}/protocol/openid-connect/userinfo"
    jwks_uri                  = "${var.dev_oidc_idp_issuer}/protocol/openid-connect/certs"
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
    authorize_url             = "${var.test_oidc_idp_issuer}/protocol/openid-connect/auth"
    token_url                 = "${var.test_oidc_idp_issuer}/protocol/openid-connect/token"
    attributes_url            = "${var.test_oidc_idp_issuer}/protocol/openid-connect/userinfo"
    jwks_uri                  = "${var.test_oidc_idp_issuer}/protocol/openid-connect/certs"
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
    authorize_url             = "${var.prod_oidc_idp_issuer}/protocol/openid-connect/auth"
    token_url                 = "${var.prod_oidc_idp_issuer}/protocol/openid-connect/token"
    attributes_url            = "${var.prod_oidc_idp_issuer}/protocol/openid-connect/userinfo"
    jwks_uri                  = "${var.prod_oidc_idp_issuer}/protocol/openid-connect/certs"
  }

  attribute_mapping = {
    email                      = "email",
    email_verified             = "email_verified",
    "custom:idp_name"          = "identity_provider",
    "custom:idp_user_id"       = "idir_user_guid",
    "custom:idp_username"      = "idir_username",
    "custom:idp_display_name"  = "display_name",
    "custom:keycloak_username" = "preferred_username"
  }

}
