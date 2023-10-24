resource "aws_cognito_user_pool_client" "dev_spar_oidc_client" {
  access_token_validity                         = "5"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = concat([
    "https://oidcdebugggersecure-c6af30-dev.apps.gold.devops.gov.bc.ca/",
    "http://localhost:3000/",
    "http://localhost:3000/silent-check-sso"
  ], [for i in range(50) : "https://nr-spar-${i}-frontend.apps.silver.devops.gov.bc.ca/"])
  logout_urls                                   = concat([
    "${var.cognito_app_client_logout_chain_url.dev}https://oidcdebugggersecure-c6af30-dev.apps.gold.devops.gov.bc.ca/",
    "${var.cognito_app_client_logout_chain_url.dev}http://localhost:3000/"
  ], [for i in range(50) : "${var.cognito_app_client_logout_chain_url.dev}https://nr-spar-${i}-frontend.apps.silver.devops.gov.bc.ca/"])
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "spar_dev"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = "${concat(var.minimum_oidc_attribute_list, ["custom:idp_display_name"])}"
  refresh_token_validity                        = "24"
  supported_identity_providers                  = [
    "${aws_cognito_identity_provider.dev_idir_oidc_provider.provider_name}",
    "${aws_cognito_identity_provider.dev_bceid_business_oidc_provider.provider_name}"
  ]

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "hours"
  }

  user_pool_id     = aws_cognito_user_pool.fam_user_pool.id
  write_attributes = "${concat(var.minimum_oidc_attribute_list, ["custom:idp_display_name"])}"
}

resource "aws_cognito_user_pool_client" "test_spar_oidc_client" {
  access_token_validity                         = "5"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = [
    "http://localhost:3000/",
    "https://oidcdebugggersecure-c6af30-dev.apps.gold.devops.gov.bc.ca/",
    "https://nr-spar-test-frontend.apps.silver.devops.gov.bc.ca/"
  ]
  logout_urls                                   = [
    "${var.cognito_app_client_logout_chain_url.test}https://nr-spar-test-frontend.apps.silver.devops.gov.bc.ca/",
    "${var.cognito_app_client_logout_chain_url.test}http://localhost:3000/"
  ]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "spar_test"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = "${concat(var.minimum_oidc_attribute_list, ["custom:idp_display_name"])}"
  refresh_token_validity                        = "24"
  supported_identity_providers                  = [
    "${aws_cognito_identity_provider.test_idir_oidc_provider.provider_name}",
    "${aws_cognito_identity_provider.test_bceid_business_oidc_provider.provider_name}"
  ]

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "hours"
  }

  user_pool_id     = aws_cognito_user_pool.fam_user_pool.id
  write_attributes = "${concat(var.minimum_oidc_attribute_list, ["custom:idp_display_name"])}"
}

resource "aws_cognito_user_pool_client" "prod_spar_oidc_client" {
  access_token_validity                         = "5"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = [
    "https://nr-spar-prod-frontend.apps.silver.devops.gov.bc.ca/"
  ]
  logout_urls                                   = [
    "${var.cognito_app_client_logout_chain_url.prod}https://nr-spar-prod-frontend.apps.silver.devops.gov.bc.ca/"
  ]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "spar_prod"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = "${concat(var.minimum_oidc_attribute_list, ["custom:idp_display_name"])}"
  refresh_token_validity                        = "24"
  supported_identity_providers                  = [
    "${aws_cognito_identity_provider.prod_idir_oidc_provider.provider_name}",
    "${aws_cognito_identity_provider.prod_bceid_business_oidc_provider.provider_name}"
  ]

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "hours"
  }

  user_pool_id     = aws_cognito_user_pool.fam_user_pool.id
  write_attributes = "${concat(var.minimum_oidc_attribute_list, ["custom:idp_display_name"])}"
}
