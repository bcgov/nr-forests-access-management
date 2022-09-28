resource "aws_cognito_user_pool_client" "fam_console_oidc_client" {
  access_token_validity                         = "60"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid"]
  callback_urls                                 = ["https://oidcdebuggersecure-3d5c3f-dev.apps.silver.devops.gov.bc.ca/"]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "fam_console"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes = ["locale", "zoneinfo", "updated_at", "custom:idp_name", "custom:idp_user_id", "custom:idp_username"]
  refresh_token_validity                        = "30"
  supported_identity_providers                  = ["${aws_cognito_identity_provider.idir_oidc_provider.provider_name}"]

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }

  user_pool_id     = aws_cognito_user_pool.fam_user_pool.id
  write_attributes = ["locale", "zoneinfo", "updated_at", "custom:idp_name", "custom:idp_user_id", "custom:idp_username"]
}

# Developer notes: we're capturing all the fields from the upstream IDP, but we really don't need them all. Only scope necessary is openid.
# It's more secure to only enable the exact fields that you need so that personal information isn't passed around in tokens unnecessarily

# Necessary list of available attributes
# read_attributes = ["locale", "zoneinfo", "updated_at", "custom:idp_name", "custom:idp_user_id", "custom:idp_username"]
# write_attributes = ["locale", "zoneinfo", "updated_at", "custom:idp_name", "custom:idp_user_id", "custom:idp_username"]

# Full list of available attributes
# read_attributes = ["address", "birthdate",  "email", "email_verified", "family_name", "gender", "given_name", "locale", "middle_name", "name", "nickname", "phone_number", "phone_number_verified", "picture", "preferred_username", "profile", "updated_at", "website", "zoneinfo", "custom:idp_display_name", "custom:idp_name", "custom:idp_user_id", "custom:idp_username"]
# write_attributes = ["address", "birthdate",  "email", "family_name", "gender", "given_name", "locale", "middle_name", "name", "nickname", "phone_number", "picture", "preferred_username", "profile", "updated_at", "website", "zoneinfo", "custom:idp_display_name", "custom:idp_name", "custom:idp_user_id", "custom:idp_username"]

 
