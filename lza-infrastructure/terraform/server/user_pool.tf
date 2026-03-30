resource "aws_cognito_user_pool" "fam_user_pool" {
  account_recovery_setting {
    recovery_mechanism {
      name     = "admin_only"
      priority = "1"
    }
  }

  admin_create_user_config {
    allow_admin_create_user_only = "true"
  }

  auto_verified_attributes = ["email"]

  email_configuration {
    email_sending_account = "COGNITO_DEFAULT"
  }

  mfa_configuration = "OFF"
  name              = var.fam_user_pool_name

  password_policy {
    minimum_length                   = "8"
    require_lowercase                = "true"
    require_numbers                  = "true"
    require_symbols                  = "true"
    require_uppercase                = "true"
    temporary_password_validity_days = "7"
  }

  schema {
    attribute_data_type      = "String"
    developer_only_attribute = "false"
    mutable                  = "true"
    name                     = "idp_name"
    required                 = "false"

    string_attribute_constraints {
      max_length = "256"
      min_length = "0"
    }
  }

  schema {
    attribute_data_type      = "String"
    developer_only_attribute = "false"
    mutable                  = "true"
    name                     = "idp_user_id"
    required                 = "false"

    string_attribute_constraints {
      max_length = "256"
      min_length = "0"
    }
  }

  schema {
    attribute_data_type      = "String"
    developer_only_attribute = "false"
    mutable                  = "true"
    name                     = "idp_username"
    required                 = "false"

    string_attribute_constraints {
      max_length = "256"
      min_length = "0"
    }
  }

  schema {
    attribute_data_type      = "String"
    developer_only_attribute = "false"
    mutable                  = "true"
    name                     = "idp_display_name"
    required                 = "false"

    string_attribute_constraints {
      max_length = "256"
      min_length = "0"
    }
  }

  schema {
    attribute_data_type      = "String"
    developer_only_attribute = "false"
    mutable                  = "true"
    name                     = "idp_business_name"
    required                 = "false"

    string_attribute_constraints {
      max_length = "2048"
      min_length = "0"
    }
  }

  schema {
    attribute_data_type      = "String"
    developer_only_attribute = "false"
    mutable                  = "true"
    name                     = "idp_business_id"
    required                 = "false"

    string_attribute_constraints {
      max_length = "2048"
      min_length = "0"
    }
  }

  schema {
    attribute_data_type      = "String"
    developer_only_attribute = "false"
    mutable                  = "true"
    name                     = "keycloak_username"
    required                 = "false"

    string_attribute_constraints {
      max_length = "2048"
      min_length = "0"
    }
  }

  schema {
    attribute_data_type      = "String"
    developer_only_attribute = "false"
    mutable                  = "true"
    name                     = "given_names"
    required                 = "false"

    string_attribute_constraints {
      max_length = "2048"
      min_length = "0"
    }
  }

  schema {
    # custom:id_token is added due to troubleshooting user pool user attributes issue.
    # This does not need to be mapped to IDP/APP Client attributes mapping.
    attribute_data_type      = "String"
    developer_only_attribute = "false"
    mutable                  = "true"
    name                     = "id_token"
    required                 = "false"

    string_attribute_constraints {
      max_length = "2048"
      min_length = "0"
    }
  }

  schema {
    # custom:access_token is added due to troubleshooting user pool user attributes issue.
    # This does not need to be mapped to IDP/APP Client attributes mapping.
    attribute_data_type      = "String"
    developer_only_attribute = "false"
    mutable                  = "true"
    name                     = "access_token"
    required                 = "false"

    string_attribute_constraints {
      max_length = "2048"
      min_length = "0"
    }
  }

  username_configuration {
    case_sensitive = "false"
  }

  verification_message_template {
    default_email_option = "CONFIRM_WITH_CODE"
  }

  lambda_config {
    pre_token_generation_config {
      lambda_arn    = aws_lambda_function.fam-auth-function.arn

      # FAM Cognito is with "Essential" Feature Plan.
      # V2_0 pre-token generation event version is included in Essential plan with better features.
      # (e.g., access token customization support)
      lambda_version = "V2_0"
    }
  }

  depends_on = [
    aws_lambda_function.fam-auth-function
  ]
}

resource "aws_cognito_user_pool_domain" "main" {
  domain       = "${var.fam_user_pool_domain_name}"
  user_pool_id = aws_cognito_user_pool.fam_user_pool.id
}

resource "aws_wafv2_web_acl_association" "fam_waf_cognito_association" {
  resource_arn = aws_cognito_user_pool.fam_user_pool.arn
  web_acl_arn  = aws_wafv2_web_acl.fam_waf_cognito.arn
  depends_on = [
    aws_wafv2_web_acl.fam_waf_cognito,
    aws_cognito_user_pool.fam_user_pool
  ]
}