resource "aws_cognito_user_pool_client" "dev_fom_ministry_oidc_client" {
  access_token_validity                         = "60"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = ["https://oidcdebuggersecure-3d5c3f-dev.apps.silver.devops.gov.bc.ca/"]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "fom_dev"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = var.minimum_read_list
  refresh_token_validity                        = "30"
  supported_identity_providers                  = [
    "${aws_cognito_identity_provider.dev_bceid_business_oidc_provider.provider_name}",
    "${aws_cognito_identity_provider.dev_bceid_business_oidc_provider.provider_name}"
  ]

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }

  user_pool_id     = aws_cognito_user_pool.fam_user_pool.id
  write_attributes = var.minimum_write_list
}

resource "aws_cognito_user_pool_client" "test_fom_ministry_oidc_client" {
  access_token_validity                         = "60"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = ["https://oidcdebuggersecure-3d5c3f-dev.apps.silver.devops.gov.bc.ca/"]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "fom_test"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = var.minimum_read_list
  refresh_token_validity                        = "30"
  supported_identity_providers                  = [
    "${aws_cognito_identity_provider.test_bceid_business_oidc_provider.provider_name}",
    "${aws_cognito_identity_provider.test_bceid_business_oidc_provider.provider_name}"
  ]

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }

  user_pool_id     = aws_cognito_user_pool.fam_user_pool.id
  write_attributes = var.minimum_write_list
}

resource "aws_cognito_user_pool_client" "prod_fom_ministry_oidc_client" {
  access_token_validity                         = "60"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = ["https://oidcdebuggersecure-3d5c3f-dev.apps.silver.devops.gov.bc.ca/"]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "fom_prod"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = var.minimum_read_list
  refresh_token_validity                        = "30"
  supported_identity_providers                  = [
    "${aws_cognito_identity_provider.prod_bceid_business_oidc_provider.provider_name}",
    "${aws_cognito_identity_provider.prod_bceid_business_oidc_provider.provider_name}"
  ]

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }

  user_pool_id     = aws_cognito_user_pool.fam_user_pool.id
  write_attributes = var.minimum_write_list
}
