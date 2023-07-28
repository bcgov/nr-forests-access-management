resource "aws_cognito_user_pool_client" "dev_silva_oidc_client" {
  access_token_validity                         = "5"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = [
    "https://oidcdebuggersecure-3d5c3f-dev.apps.silver.devops.gov.bc.ca/",
    "http://localhost:3000/dashboard",
    "http://localhost:8080/",
    "http://localhost:3000/login"
  ]
  logout_urls                                   = [
    "${var.cognito_app_client_logout_chain_url.dev}https://oidcdebuggersecure-3d5c3f-dev.apps.silver.devops.gov.bc.ca/",
    "${var.cognito_app_client_logout_chain_url.dev}http://localhost:3000/",
    "${var.cognito_app_client_logout_chain_url.dev}http://localhost:3000/logout"
  ]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "silva_dev"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = "${concat(var.minimum_oidc_attribute_list, ["custom:idp_display_name"])}"
  refresh_token_validity                        = "24"
  supported_identity_providers                  = [
    "${aws_cognito_identity_provider.dev_idir_oidc_provider.provider_name}"
  ]

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "hours"
  }

  user_pool_id     = aws_cognito_user_pool.fam_user_pool.id
  write_attributes = "${concat(var.minimum_oidc_attribute_list, ["custom:idp_display_name"])}"
}

resource "aws_cognito_user_pool_client" "test_silva_oidc_client" {
  access_token_validity                         = "5"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = [
    "https://oidcdebuggersecure-3d5c3f-dev.apps.silver.devops.gov.bc.ca/",
    "http://localhost:3000/dashboard",
    "http://localhost:8080/",
    "http://localhost:3000/login"
  ]
  logout_urls                                   = [
    "${var.cognito_app_client_logout_chain_url.test}https://oidcdebuggersecure-3d5c3f-dev.apps.silver.devops.gov.bc.ca/",
    "${var.cognito_app_client_logout_chain_url.test}http://localhost:3000/",
    "${var.cognito_app_client_logout_chain_url.test}http://localhost:3000/logout"
  ]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "silva_test"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = "${concat(var.minimum_oidc_attribute_list, ["custom:idp_display_name"])}"
  refresh_token_validity                        = "24"
  supported_identity_providers                  = [
    "${aws_cognito_identity_provider.test_idir_oidc_provider.provider_name}"
  ]

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "hours"
  }

  user_pool_id     = aws_cognito_user_pool.fam_user_pool.id
  write_attributes = "${concat(var.minimum_oidc_attribute_list, ["custom:idp_display_name"])}"
}

resource "aws_cognito_user_pool_client" "prod_silva_oidc_client" {
  access_token_validity                         = "5"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = [
    "https://oidcdebuggersecure-3d5c3f-dev.apps.silver.devops.gov.bc.ca/",
    "http://localhost:3000/dashboard",
    "http://localhost:8080/",
    "http://localhost:3000/login"
  ]
  logout_urls                                   = [
    "${var.cognito_app_client_logout_chain_url.prod}https://oidcdebuggersecure-3d5c3f-dev.apps.silver.devops.gov.bc.ca/",
    "${var.cognito_app_client_logout_chain_url.prod}http://localhost:3000/",
    "${var.cognito_app_client_logout_chain_url.prod}http://localhost:3000/logout"
  ]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "silva_prod"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = "${concat(var.minimum_oidc_attribute_list, ["custom:idp_display_name"])}"
  refresh_token_validity                        = "24"
  supported_identity_providers                  = [
    "${aws_cognito_identity_provider.prod_idir_oidc_provider.provider_name}"
  ]

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "hours"
  }

  user_pool_id     = aws_cognito_user_pool.fam_user_pool.id
  write_attributes = "${concat(var.minimum_oidc_attribute_list, ["custom:idp_display_name"])}"
}
