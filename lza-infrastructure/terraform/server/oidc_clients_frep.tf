resource "aws_cognito_user_pool_client" "dev_frep_oidc_client" {
  access_token_validity                         = "5"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = concat(
      [
        var.oidc_sso_playground_url,
        "http://localhost:3000/welcome",
      ],
      [for i in range("${var.dev_pr_url_count}") : "https://nr-frep-${i}.apps.silver.devops.gov.bc.ca/welcome"]
  )
  logout_urls                                   = concat(
      [
        var.oidc_sso_playground_url,
        "${var.cognito_app_client_logout_chain_url.dev}http://localhost:3000",
      ],
      [for i in range("${var.dev_pr_url_count}") : "${var.cognito_app_client_logout_chain_url.dev}https://nr-frep-${i}.apps.silver.devops.gov.bc.ca"]
  )
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "5"
  name                                          = "frep_dev"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = var.minimum_oidc_attribute_list
  refresh_token_validity                        = "60"
  supported_identity_providers                  = [
    "${aws_cognito_identity_provider.dev_idir_oidc_provider.provider_name}",
    "${aws_cognito_identity_provider.dev_bceid_business_oidc_provider.provider_name}"
  ]

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "minutes"
  }

  user_pool_id     = aws_cognito_user_pool.fam_user_pool.id
  write_attributes = var.minimum_oidc_attribute_list
}

resource "aws_cognito_user_pool_client" "test_frep_oidc_client" {
  access_token_validity                         = "5"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = [
    "https://nr-frep-test.apps.silver.devops.gov.bc.ca/welcome"
  ]
  logout_urls                                   = [
    "${var.cognito_app_client_logout_chain_url.test}https://nr-frep-test.apps.silver.devops.gov.bc.ca"
  ]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "5"
  name                                          = "frep_test"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = var.minimum_oidc_attribute_list
  refresh_token_validity                        = "60"
  supported_identity_providers                  = [
    "${aws_cognito_identity_provider.test_idir_oidc_provider.provider_name}",
    "${aws_cognito_identity_provider.test_bceid_business_oidc_provider.provider_name}"
  ]

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "minutes"
  }

  user_pool_id     = aws_cognito_user_pool.fam_user_pool.id
  write_attributes = var.minimum_oidc_attribute_list
}

resource "aws_cognito_user_pool_client" "prod_frep_oidc_client" {
  access_token_validity                         = "5"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = [
    "https://nr-frep-prod.apps.silver.devops.gov.bc.ca/welcome"
  ]
  logout_urls                                   = [
    "${var.cognito_app_client_logout_chain_url.prod}https://nr-frep-prod.apps.silver.devops.gov.bc.ca"
  ]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "5"
  name                                          = "frep_prod"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = var.minimum_oidc_attribute_list
  refresh_token_validity                        = "60"
  supported_identity_providers                  = [
    "${aws_cognito_identity_provider.prod_idir_oidc_provider.provider_name}",
    "${aws_cognito_identity_provider.prod_bceid_business_oidc_provider.provider_name}"
  ]

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "minutes"
  }

  user_pool_id     = aws_cognito_user_pool.fam_user_pool.id
  write_attributes = var.minimum_oidc_attribute_list
}
