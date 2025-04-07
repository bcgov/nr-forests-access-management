resource "aws_cognito_user_pool_client" "dev_apt_oidc_client" {
  access_token_validity                         = "5"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = [
    var.oidc_sso_playground_url,
    "http://localhost:8080/apt2/callback",
    "https://dlvrapps.nrs.gov.bc.ca/int/apt2/callback"
  ]
  logout_urls                                   = [
    var.oidc_sso_playground_url,
    "${var.cognito_app_client_logout_chain_url.dev}http://localhost:8080/",
    "${var.cognito_app_client_logout_chain_url.dev}https://dlvrapps.nrs.gov.bc.ca/int/apt2"
  ]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "apt_dev"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = "${concat(var.minimum_oidc_attribute_list, ["custom:idp_display_name", "email"])}"
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
  write_attributes = "${concat(var.minimum_oidc_attribute_list, ["custom:idp_display_name", "email"])}"
}

resource "aws_cognito_user_pool_client" "test_apt_oidc_client" {
  access_token_validity                         = "5"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = [
      var.oidc_sso_playground_url,
      "http://localhost:8080/apt2/callback",
      "https://testapps.nrs.gov.bc.ca/int/apt2/callback"
    ]
  logout_urls                                   = [
      var.oidc_sso_playground_url,
      "${var.cognito_app_client_logout_chain_url.test}http://localhost:8080/",
      "${var.cognito_app_client_logout_chain_url.test}https://testapps.nrs.gov.bc.ca/int/apt2"
    ]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "apt_test"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = "${concat(var.minimum_oidc_attribute_list, ["custom:idp_display_name", "email"])}"
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
  write_attributes = "${concat(var.minimum_oidc_attribute_list, ["custom:idp_display_name", "email"])}"
}

resource "aws_cognito_user_pool_client" "prod_apt_oidc_client" {
  access_token_validity                         = "5"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = [
    var.oidc_sso_playground_url,
    "https://apps.nrs.gov.bc.ca/int/apt2/callback"
  ]
  logout_urls                                   = [
    var.oidc_sso_playground_url,
    "${var.cognito_app_client_logout_chain_url.prod}https://apps.nrs.gov.bc.ca/int/apt2"
  ]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "apt_prod"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = "${concat(var.minimum_oidc_attribute_list, ["custom:idp_display_name", "email"])}"
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
  write_attributes = "${concat(var.minimum_oidc_attribute_list, ["custom:idp_display_name", "email"])}"
}
