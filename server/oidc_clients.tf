resource "aws_cognito_user_pool_client" "fam_console_oidc_client" {
  access_token_validity                         = "60"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = ["https://oidcdebuggersecure-3d5c3f-dev.apps.silver.devops.gov.bc.ca/"]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "fam_console"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = var.minimum_read_list
  refresh_token_validity                        = "30"
  supported_identity_providers                  = ["${aws_cognito_identity_provider.idir_oidc_provider.provider_name}"]

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }

  user_pool_id     = aws_cognito_user_pool.fam_user_pool.id
  write_attributes = var.minimum_write_list
}

resource "aws_cognito_user_pool_client" "fom_ministry_oidc_client" {
  access_token_validity                         = "60"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = ["https://oidcdebuggersecure-3d5c3f-dev.apps.silver.devops.gov.bc.ca/"]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "fom_ministry"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = var.all_read_list_idir
  refresh_token_validity                        = "30"
  supported_identity_providers                  = ["${aws_cognito_identity_provider.idir_oidc_provider.provider_name}"]

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }

  user_pool_id     = aws_cognito_user_pool.fam_user_pool.id
  write_attributes = var.all_write_list_idir
}


resource "aws_cognito_user_pool_client" "fom_public_oidc_client" {
  access_token_validity                         = "60"
  allowed_oauth_flows                           = ["code"]
  allowed_oauth_flows_user_pool_client          = "true"
  allowed_oauth_scopes                          = ["openid", "profile", "email"]
  callback_urls                                 = ["https://oidcdebuggersecure-3d5c3f-dev.apps.silver.devops.gov.bc.ca/"]
  enable_propagate_additional_user_context_data = "false"
  enable_token_revocation                       = "true"
  explicit_auth_flows                           = ["ALLOW_REFRESH_TOKEN_AUTH"]
  id_token_validity                             = "60"
  name                                          = "fom_public"
  prevent_user_existence_errors                 = "ENABLED"
  read_attributes                               = var.all_read_list_bceid_business
  refresh_token_validity                        = "30"
  supported_identity_providers                  = ["${aws_cognito_identity_provider.bceid_business_oidc_provider.provider_name}"]

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }

  user_pool_id     = aws_cognito_user_pool.fam_user_pool.id
  write_attributes = var.all_write_list_bceid_business
}

# Developer notes: we're capturing all the fields from the upstream IDP, but we really don't need them all. Only scope necessary is openid.
# It's more secure to only enable the exact fields that you need so that personal information isn't passed around in tokens unnecessarily

variable "minimum_read_list" {
  description = "The list of required read attributes for all clients"
  type        = list(string)
  default     = ["custom:idp_name", "custom:idp_user_id", "custom:idp_username"]
}

variable "minimum_write_list" {
  description = "The list of required write attributes for all clients"
  type        = list(string)
  default     = ["email", "custom:idp_name", "custom:idp_user_id", "custom:idp_username"]
}

variable "all_read_list_idir" {
  description = "The list of all read attributes for IDIR clients"
  type        = list(string)
  default     = ["email", "email_verified", "name" "family_name", "given_name", "preferred_username", "profile", "custom:idp_display_name", "custom:idp_name", "custom:idp_user_id", "custom:idp_username"]
}

variable "all_write_list_idir" {
  description = "The list of all write attributes for IDIR clients"
  type        = list(string)
  default     = ["email", "name", "family_name", "given_name", "preferred_username", "profile", "custom:idp_display_name", "custom:idp_name", "custom:idp_user_id", "custom:idp_username"]
}

variable "all_read_list_bceid_business" {
  description = "The list of all read attributes for BCEIDBUSINESS clients"
  type        = list(string)
  default     = ["email", "email_verified", "preferred_username", "profile", "custom:idp_display_name", "custom:idp_name", "custom:idp_user_id", "custom:idp_username", "custom:idp_business_name", "custom:idp_business_id"]
}

variable "all_write_list_bceid_business" {
  description = "The list of all write attributes for BCEIDBUSINESS clients"
  type        = list(string)
  default     = ["email", "preferred_username", "profile", "custom:idp_display_name", "custom:idp_name", "custom:idp_user_id", "custom:idp_username", "custom:idp_business_name", "custom:idp_business_id"]
}
