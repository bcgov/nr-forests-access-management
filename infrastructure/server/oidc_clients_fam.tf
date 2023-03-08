resource "aws_cognito_user_pool_client" "fam_console_oidc_client" {
  access_token_validity                = "5"
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_flows_user_pool_client = "true"
  allowed_oauth_scopes                 = ["openid", "profile", "email"]
  callback_urls                        = var.fam_callback_urls
  logout_urls                          = var.fam_logout_urls
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "fam_console"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = var.minimum_read_list
  refresh_token_validity                        = "24"
  supported_identity_providers                  = [ var.fam_console_idp_name ]

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "hours"
  }

  user_pool_id     = aws_cognito_user_pool.fam_user_pool.id
  write_attributes = var.minimum_write_list

  depends_on = [
    aws_cognito_identity_provider.dev_idir_oidc_provider,
    aws_cognito_identity_provider.test_idir_oidc_provider,
    aws_cognito_identity_provider.prod_idir_oidc_provider
  ]
}

# Need to write the client ID to an AWS Secret so that the API lambda can
# read it at run time. At build time, specifying it as an env variable will
# create a dependency cycle

resource "random_pet" "fam_oidc_client_id_secret_name" {
  prefix = "fam_oidc_id"
  length = 2
}

resource "aws_secretsmanager_secret" "fam_oidc_client_id_secret" {
  name = random_pet.fam_oidc_client_id_secret_name.id

  tags = {
    managed-by = "terraform"
  }
}

resource "aws_secretsmanager_secret_version" "fam_oidc_client_id_secret_version" {
  secret_id     = aws_secretsmanager_secret.fam_oidc_client_id_secret.id
  secret_string = aws_cognito_user_pool_client.fam_console_oidc_client.id
}