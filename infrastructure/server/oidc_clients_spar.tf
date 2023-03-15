resource "aws_cognito_user_pool_client" "dev_spar_oidc_client" {
  access_token_validity                         = "5"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = [
    "https://oidcdebuggersecure-3d5c3f-dev.apps.silver.devops.gov.bc.ca/",
    "http://localhost:3000/dashboard",
    "http://localhost:3000/silent-check-sso"
  ]
  logout_urls                                   = [
    "${var.frontend_logout_chain_url}https://oidcdebuggersecure-3d5c3f-dev.apps.silver.devops.gov.bc.ca/",
    "${var.frontend_logout_chain_url}http://localhost:3000/"
  ]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "spar_dev"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = "${concat(var.minimum_read_list, ["custom:idp_display_name"])}"
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
  write_attributes = "${concat(var.minimum_write_list, ["custom:idp_display_name"])}"
}

resource "aws_cognito_user_pool_client" "test_spar_oidc_client" {
  access_token_validity                         = "5"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = [
    "https://oidcdebuggersecure-3d5c3f-dev.apps.silver.devops.gov.bc.ca/",
    "https://nr-spar-webapp-test-frontend.apps.silver.devops.gov.bc.ca/dashboard"
  ]
  logout_urls                                   = [
    "${var.frontend_logout_chain_url}https://nr-spar-webapp-test-frontend.apps.silver.devops.gov.bc.ca/"
  ]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "spar_test"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = "${concat(var.minimum_read_list, ["custom:idp_display_name"])}"
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
  write_attributes = "${concat(var.minimum_write_list, ["custom:idp_display_name"])}"
}

resource "aws_cognito_user_pool_client" "prod_spar_oidc_client" {
  access_token_validity                         = "5"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = [
    "https://nr-spar-webapp-test-frontend.apps.silver.devops.gov.bc.ca/dashboard"
  ]
  logout_urls                                   = [
    "${var.frontend_logout_chain_url}https://nr-spar-webapp-test-frontend.apps.silver.devops.gov.bc.ca/"
  ]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "spar_prod"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = "${concat(var.minimum_read_list, ["custom:idp_display_name"])}"
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
  write_attributes = "${concat(var.minimum_write_list, ["custom:idp_display_name"])}"
}
