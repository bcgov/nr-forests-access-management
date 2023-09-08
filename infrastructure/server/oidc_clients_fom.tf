resource "aws_cognito_user_pool_client" "dev_fom_oidc_client" {
  access_token_validity                         = "5"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = [
    "https://oidcdebugggersecure-c6af30-dev.apps.gold.devops.gov.bc.ca/",
    "http://localhost:4200/admin/search"
  ]
  logout_urls                                   = [
    "${var.cognito_app_client_logout_chain_url.dev}http://localhost:4200/admin/not-authorized?loggedout=true"
  ]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "fom_dev"
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

resource "aws_cognito_user_pool_client" "test_fom_oidc_client" {
  access_token_validity                         = "5"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = [
    "https://oidcdebugggersecure-c6af30-dev.apps.gold.devops.gov.bc.ca/",
    "https://fom-test.nrs.gov.bc.ca/admin/search",
    "https://fom-demo.apps.silver.devops.gov.bc.ca/admin/search",
    "http://localhost:4200/admin/search"
  ]
  logout_urls                                   = [
    "${var.cognito_app_client_logout_chain_url.test}https://fom-test.nrs.gov.bc.ca/admin/not-authorized?loggedout=true",
    "${var.cognito_app_client_logout_chain_url.test}https://fom-demo.apps.silver.devops.gov.bc.ca/admin/not-authorized?loggedout=true"
  ]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "fom_test"
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

resource "aws_cognito_user_pool_client" "prod_fom_oidc_client" {
  access_token_validity                         = "5"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = [
    "https://fom.nrs.gov.bc.ca/admin/search",
  ]
  logout_urls                                   = [
    "${var.cognito_app_client_logout_chain_url.prod}https://fom.nrs.gov.bc.ca/admin/not-authorized?loggedout=true"
  ]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "fom_prod"
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
