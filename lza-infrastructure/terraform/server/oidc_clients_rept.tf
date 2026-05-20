resource "aws_cognito_user_pool_client" "dev_rept_oidc_client" {
  access_token_validity                         = "5"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = [
    var.oidc_sso_playground_url,
    "http://localhost:3000/dashboard",
    "https://nr-rept-0.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-1.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-2.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-3.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-4.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-5.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-6.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-7.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-8.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-9.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-10.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-11.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-12.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-13.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-14.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-15.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-16.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-17.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-18.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-19.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-20.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-21.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-22.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-23.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-24.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-25.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-26.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-27.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-28.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-29.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-30.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-31.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-32.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-33.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-34.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-35.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-36.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-37.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-38.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-39.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-40.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-41.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-42.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-43.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-44.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-45.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-46.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-47.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-48.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-49.apps.silver.devops.gov.bc.ca/dashboard",
    "https://nr-rept-50.apps.silver.devops.gov.bc.ca/dashboard"
  ]
  logout_urls                                   = [
    var.oidc_sso_playground_url,
    "${var.cognito_app_client_logout_chain_url.dev}http://localhost:3000",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-0.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-1.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-2.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-3.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-4.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-5.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-6.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-7.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-8.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-9.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-10.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-11.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-12.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-13.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-14.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-15.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-16.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-17.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-18.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-19.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-20.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-21.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-22.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-23.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-24.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-25.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-26.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-27.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-28.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-29.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-30.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-31.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-32.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-33.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-34.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-35.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-36.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-37.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-38.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-39.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-40.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-41.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-42.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-43.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-44.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-45.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-46.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-47.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-48.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-49.apps.silver.devops.gov.bc.ca",
    "${var.cognito_app_client_logout_chain_url.dev}https://nr-rept-50.apps.silver.devops.gov.bc.ca",
  ]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "5"
  name                                          = "rept_dev"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = var.minimum_oidc_attribute_list
  refresh_token_validity                        = "60"
  supported_identity_providers                  = [
    "${aws_cognito_identity_provider.dev_idir_oidc_provider.provider_name}"
  ]

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "minutes"
  }

  user_pool_id     = aws_cognito_user_pool.fam_user_pool.id
  write_attributes = var.minimum_oidc_attribute_list
}

resource "aws_cognito_user_pool_client" "test_rept_oidc_client" {
  access_token_validity                         = "5"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = [
    "https://nr-rept-test.apps.silver.devops.gov.bc.ca/dashboard"
  ]
  logout_urls                                   = [
    "${var.cognito_app_client_logout_chain_url.test}https://nr-rept-test.apps.silver.devops.gov.bc.ca"
  ]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "5"
  name                                          = "rept_test"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = var.minimum_oidc_attribute_list
  refresh_token_validity                        = "60"
  supported_identity_providers                  = [
    "${aws_cognito_identity_provider.test_idir_oidc_provider.provider_name}"
  ]

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "minutes"
  }

  user_pool_id     = aws_cognito_user_pool.fam_user_pool.id
  write_attributes = var.minimum_oidc_attribute_list
}

resource "aws_cognito_user_pool_client" "prod_rept_oidc_client" {
  access_token_validity                         = "5"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = [
    "https://nr-rept-prod.apps.silver.devops.gov.bc.ca/dashboard"
  ]
  logout_urls                                   = [
    "${var.cognito_app_client_logout_chain_url.prod}https://nr-rept-prod.apps.silver.devops.gov.bc.ca"
  ]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "5"
  name                                          = "rept_prod"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = var.minimum_oidc_attribute_list
  refresh_token_validity                        = "60"
  supported_identity_providers                  = [
    "${aws_cognito_identity_provider.prod_idir_oidc_provider.provider_name}"
  ]

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "minutes"
  }

  user_pool_id     = aws_cognito_user_pool.fam_user_pool.id
  write_attributes = var.minimum_oidc_attribute_list
}
