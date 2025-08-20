# BCSC IDP that connects directly to IDIM Consulting OIDC server
locals {
  dev_local_bcsc_userinfo_proxy_endpoint  = "${aws_api_gateway_deployment.fam_api_gateway_deployment.invoke_url}/bcsc/userinfo/dev"
  test_local_bcsc_userinfo_proxy_endpoint = "${aws_api_gateway_deployment.fam_api_gateway_deployment.invoke_url}/bcsc/userinfo/test"
  prod_local_bcsc_userinfo_proxy_endpoint = "${aws_api_gateway_deployment.fam_api_gateway_deployment.invoke_url}/bcsc/userinfo/prod"
  dev_local_bcsc_token_proxy_endpoint     = "${aws_api_gateway_deployment.fam_api_gateway_deployment.invoke_url}/bcsc/token/dev"
  test_local_bcsc_token_proxy_endpoint    = "${aws_api_gateway_deployment.fam_api_gateway_deployment.invoke_url}/bcsc/token/test"
  prod_local_bcsc_token_proxy_endpoint    = "${aws_api_gateway_deployment.fam_api_gateway_deployment.invoke_url}/bcsc/token/prod"
}

resource "aws_cognito_identity_provider" "dev_bcsc_oidc_provider" {
  user_pool_id  = aws_cognito_user_pool.fam_user_pool.id
  provider_name = "DEV-BCSC"
  provider_type = "OIDC"

  provider_details = {
    authorize_scopes          = "openid profile email address"
    client_id                 = var.dev_oidc_bcsc_idp_client_id
    client_secret             = var.dev_oidc_bcsc_idp_client_secret
    oidc_issuer               = var.dev_bcsc_oidc_idp_issuer
    attributes_request_method = "GET"
    authorize_url             = "https://idtest.gov.bc.ca/login/oidc/authorize"
    token_url                 = "${var.use_override_proxy_endpoints ? var.dev_override_bcsc_token_proxy_endpoint : local.dev_local_bcsc_token_proxy_endpoint}"
    attributes_url            = "${var.use_override_proxy_endpoints ? var.dev_override_bcsc_userinfo_proxy_endpoint : local.dev_local_bcsc_userinfo_proxy_endpoint}"
    jwks_uri                  = "https://idtest.gov.bc.ca/oauth2/jwk"
  }

  attribute_mapping = {
    given_name                = "given_name",
    family_name               = "family_name",
    birthdate                 = "birthdate",
    email                     = "email",
    email_verified            = "email_verified",
    address                   = "address",
    "custom:idp_name"         = "aud",
    "custom:idp_user_id"      = "sub",
    "custom:idp_display_name" = "display_name",
    "custom:given_names"      = "given_names"
  }
}

resource "aws_cognito_identity_provider" "test_bcsc_oidc_provider" {
  user_pool_id  = aws_cognito_user_pool.fam_user_pool.id
  provider_name = "TEST-BCSC"
  provider_type = "OIDC"

  provider_details = {
    authorize_scopes          = "openid profile email address"
    client_id                 = var.test_oidc_bcsc_idp_client_id
    client_secret             = var.test_oidc_bcsc_idp_client_secret
    oidc_issuer               = var.test_bcsc_oidc_idp_issuer
    attributes_request_method = "GET"
    authorize_url             = "https://idtest.gov.bc.ca/login/oidc/authorize"
    token_url                 = "${var.use_override_proxy_endpoints ? var.test_override_bcsc_token_proxy_endpoint : local.test_local_bcsc_token_proxy_endpoint}"
    attributes_url            = "${var.use_override_proxy_endpoints ? var.test_override_bcsc_userinfo_proxy_endpoint : local.test_local_bcsc_userinfo_proxy_endpoint}"
    jwks_uri                  = "https://idtest.gov.bc.ca/oauth2/jwk"
  }

  attribute_mapping = {
    given_name                = "given_name",
    family_name               = "family_name",
    birthdate                 = "birthdate",
    email                     = "email",
    email_verified            = "email_verified",
    address                   = "address",
    "custom:idp_name"         = "aud",
    "custom:idp_user_id"      = "sub",
    "custom:idp_display_name" = "display_name",
    "custom:given_names"      = "given_names"
  }

}

resource "aws_cognito_identity_provider" "prod_bcsc_oidc_provider" {
  user_pool_id  = aws_cognito_user_pool.fam_user_pool.id
  provider_name = "PROD-BCSC"
  provider_type = "OIDC"

  provider_details = {
    authorize_scopes          = "openid profile email address"
    client_id                 = var.prod_oidc_bcsc_idp_client_id
    client_secret             = var.prod_oidc_bcsc_idp_client_secret
    oidc_issuer               = var.prod_bcsc_oidc_idp_issuer
    attributes_request_method = "GET"
    authorize_url             = "https://id.gov.bc.ca/login/oidc/authorize"
    token_url                 = "${var.use_override_proxy_endpoints ? var.prod_override_bcsc_token_proxy_endpoint : local.prod_local_bcsc_token_proxy_endpoint}"
    attributes_url            = "${var.use_override_proxy_endpoints ? var.prod_override_bcsc_userinfo_proxy_endpoint : local.prod_local_bcsc_userinfo_proxy_endpoint}"
    jwks_uri                  = "https://id.gov.bc.ca/oauth2/jwk"
  }

  attribute_mapping = {
    given_name                = "given_name",
    family_name               = "family_name",
    birthdate                 = "birthdate",
    email                     = "email",
    email_verified            = "email_verified",
    address                   = "address",
    "custom:idp_display_name" = "display_name",
    "custom:idp_name"         = "aud",
    "custom:idp_user_id"      = "sub",
    "custom:given_names"      = "given_names"
  }

}
