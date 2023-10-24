resource "aws_cognito_user_pool_client" "dev_forest_client_oidc_client" {
  access_token_validity                = "5"
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_flows_user_pool_client = "true"
  allowed_oauth_scopes                 = ["openid", "profile", "email"]
  callback_urls = concat([
    "https://oidcdebugggersecure-c6af30-dev.apps.gold.devops.gov.bc.ca/",
    "http://localhost:3000/dashboard",
  ], [for i in range(50) : "https://nr-forest-client-${i}-frontend.apps.silver.devops.gov.bc.ca/dashboard"])
  logout_urls = concat([
    "${var.cognito_app_client_logout_chain_url.dev}http://localhost:3000/"
  ], [for i in range(50) : "${var.cognito_app_client_logout_chain_url.dev}https://nr-forest-client-${i}-frontend.apps.silver.devops.gov.bc.ca/"])
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "forest_client_dev"
  prevent_user_existence_errors                 = "ENABLED"
  # read_attributes        = "${concat(var.minimum_oidc_attribute_list, ["custom:idp_display_name", "email"])}"

  read_attributes        = var.maximum_oidc_attribute_read_list
  refresh_token_validity = "24"
  supported_identity_providers = [
    "${aws_cognito_identity_provider.dev_bcsc_oidc_provider.provider_name}",
    "${aws_cognito_identity_provider.dev_bceid_business_oidc_provider.provider_name}",
    "${aws_cognito_identity_provider.dev_idir_oidc_provider.provider_name}"
  ]

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "hours"
  }

  user_pool_id = aws_cognito_user_pool.fam_user_pool.id
  # write_attributes = "${concat(var.minimum_oidc_attribute_list, ["custom:idp_display_name", "email"])}"
  write_attributes = var.maximum_oidc_attribute_write_list
}

resource "aws_cognito_user_pool_client" "test_forest_client_oidc_client" {
  access_token_validity                = "5"
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_flows_user_pool_client = "true"
  allowed_oauth_scopes                 = ["openid", "profile", "email"]
  callback_urls = [
    "https://oidcdebugggersecure-c6af30-dev.apps.gold.devops.gov.bc.ca/",
    "http://localhost:3000/dashboard",
    "https://nr-forest-client-test-frontend.apps.silver.devops.gov.bc.ca/dashboard"
  ]
  logout_urls = [
    "http://localhost:3000/",
    "${var.cognito_app_client_logout_chain_url.test}https://nr-forest-client-test-frontend.apps.silver.devops.gov.bc.ca/"
  ]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "forest_client_test"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = var.maximum_oidc_attribute_read_list
  refresh_token_validity                        = "24"
  supported_identity_providers = [
    "${aws_cognito_identity_provider.test_bcsc_oidc_provider.provider_name}",
    "${aws_cognito_identity_provider.test_bceid_business_oidc_provider.provider_name}",
    "${aws_cognito_identity_provider.test_idir_oidc_provider.provider_name}"
  ]

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "hours"
  }

  user_pool_id     = aws_cognito_user_pool.fam_user_pool.id
  write_attributes = var.maximum_oidc_attribute_write_list
}

resource "aws_cognito_user_pool_client" "prod_forest_client_oidc_client" {
  access_token_validity                = "5"
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_flows_user_pool_client = "true"
  allowed_oauth_scopes                 = ["openid", "profile", "email"]
  callback_urls = [
    "https://oidcdebugggersecure-c6af30-dev.apps.gold.devops.gov.bc.ca/",
    "http://localhost:3000/dashboard",
    "https://nr-forest-client-prod-frontend.apps.silver.devops.gov.bc.ca/dashboard"
  ]
  logout_urls = [
    "http://localhost:3000/",
    "${var.cognito_app_client_logout_chain_url.prod}https://nr-forest-client-prod-frontend.apps.silver.devops.gov.bc.ca/"
  ]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "forest_client_prod"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = var.maximum_oidc_attribute_read_list
  refresh_token_validity                        = "24"
  supported_identity_providers = [
    "${aws_cognito_identity_provider.prod_bcsc_oidc_provider.provider_name}",
    "${aws_cognito_identity_provider.prod_bceid_business_oidc_provider.provider_name}",
    "${aws_cognito_identity_provider.prod_idir_oidc_provider.provider_name}"
  ]

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "hours"
  }

  user_pool_id     = aws_cognito_user_pool.fam_user_pool.id
  write_attributes = var.maximum_oidc_attribute_write_list
}
