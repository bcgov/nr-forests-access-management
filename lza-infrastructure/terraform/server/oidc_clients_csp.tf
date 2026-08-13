locals {
  csp_dev_host_urls = [
    for i in range(var.dev_pr_url_count) : "https://nr-csp-${i}.apps.gold.devops.gov.bc.ca"
  ]

  csp_test_host_urls = [
    "https://nr-csp-test.apps.gold.devops.gov.bc.ca"
  ]

  csp_prod_host_urls = [
    "https://nr-csp-prod.apps.gold.devops.gov.bc.ca"
  ]
}

resource "aws_cognito_user_pool_client" "dev_csp_oidc_client" {
  access_token_validity                = "5"
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_flows_user_pool_client = "true"
  allowed_oauth_scopes                 = ["openid", "profile", "email"]
  callback_urls = concat(
    [
      var.oidc_sso_playground_url,
      "http://localhost:3000/"
    ],
    local.csp_dev_host_urls
  )
  # Plain <app>/logout URLs support the app-driven federated logout chain
  # (Siteminder -> Keycloak -> Cognito -> app, as in FAM's own logoutChain.ts),
  # where Cognito fires last and returns the user to the app. PR host urls are
  # swapped from chain-prefixed to plain (rather than added) to stay under the
  # 100 sign-out URLs per app client quota (1 + 2 + 2x50 would exceed it).
  logout_urls = concat(
    [
      var.oidc_sso_playground_url,
      "${var.cognito_app_client_logout_chain_url.dev}http://localhost:3000/logout",
      "http://localhost:3000/logout",
    ],
    [
      for url in local.csp_dev_host_urls :
      "${url}/logout"
    ]
  )
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "5"
  name                                          = "csp_dev"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = var.minimum_oidc_attribute_list
  refresh_token_validity                        = "60"
  supported_identity_providers = [
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

resource "aws_cognito_user_pool_client" "test_csp_oidc_client" {
  access_token_validity                = "5"
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_flows_user_pool_client = "true"
  allowed_oauth_scopes                 = ["openid", "profile", "email"]
  callback_urls                        = concat([var.oidc_sso_playground_url], local.csp_test_host_urls)
  logout_urls = concat(
    [var.oidc_sso_playground_url],
    [for url in local.csp_test_host_urls : "${var.cognito_app_client_logout_chain_url.test}${url}/logout"],
    [for url in local.csp_test_host_urls : "${url}/logout"]
  )
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "5"
  name                                          = "csp_test"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = var.minimum_oidc_attribute_list
  refresh_token_validity                        = "60"
  supported_identity_providers = [
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

resource "aws_cognito_user_pool_client" "prod_csp_oidc_client" {
  access_token_validity                = "5"
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_flows_user_pool_client = "true"
  allowed_oauth_scopes                 = ["openid", "profile", "email"]
  callback_urls                        = concat([var.oidc_sso_playground_url], local.csp_prod_host_urls)
  logout_urls = concat(
    [var.oidc_sso_playground_url],
    [for url in local.csp_prod_host_urls : "${var.cognito_app_client_logout_chain_url.prod}${url}/logout"],
    [for url in local.csp_prod_host_urls : "${url}/logout"]
  )
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "5"
  name                                          = "csp_prod"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = var.minimum_oidc_attribute_list
  refresh_token_validity                        = "60"
  supported_identity_providers = [
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
