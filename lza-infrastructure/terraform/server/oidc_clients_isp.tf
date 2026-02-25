resource "aws_cognito_user_pool_client" "dev_isp_oidc_client" {
  access_token_validity                         = "5"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = [
    var.oidc_sso_playground_url,
    "http://localhost:3000/",
    "https://dlvrapps.nrs.gov.bc.ca/int/isp/callback"
  ]
  logout_urls                                   = [
    var.oidc_sso_playground_url,
    "${var.cognito_app_client_logout_chain_url.dev}http://localhost:3000",
    "${var.cognito_app_client_logout_chain_url.dev}https://dlvrapps.nrs.gov.bc.ca/int/isp"
  ]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "isp_dev"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = var.minimum_oidc_attribute_list
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
  write_attributes = var.minimum_oidc_attribute_list
}

resource "aws_cognito_user_pool_client" "test_isp_oidc_client" {
  access_token_validity                         = "5"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = [
    var.oidc_sso_playground_url,
    "http://localhost:8080/isp/callback",
    "https://testapps.nrs.gov.bc.ca/int/isp/callback"
  ]
  logout_urls                                   = [
    var.oidc_sso_playground_url,
    "${var.cognito_app_client_logout_chain_url.test}http://localhost:8000",
    "${var.cognito_app_client_logout_chain_url.test}https://testapps.nrs.gov.bc.ca/int/isp"
  ]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "isp_test"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = var.minimum_oidc_attribute_list
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
  write_attributes = var.minimum_oidc_attribute_list
}

resource "aws_cognito_user_pool_client" "prod_isp_oidc_client" {
  access_token_validity                         = "5"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = [
    var.oidc_sso_playground_url,
    "https://apps.nrs.gov.bc.ca/int/isp/callback"
  ]
  logout_urls                                   = [
    var.oidc_sso_playground_url,
    "${var.cognito_app_client_logout_chain_url.prod}https://apps.nrs.gov.bc.ca/int/isp"
  ]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "isp_prod"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = var.minimum_oidc_attribute_list
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
  write_attributes = var.minimum_oidc_attribute_list
}
