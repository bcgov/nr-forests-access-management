resource "random_pet" "fam_user_pool_name" {
  prefix = "fam-user-pool"
  length = 2
}

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

  #   lambda_config {
  #     pre_token_generation = "arn:aws:lambda:ca-central-1:521834415778:function:testCognitoPreJWT"
  #   }

  mfa_configuration = "OFF"
  name              = random_pet.fam_user_pool_name.id

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
    name                     = "display_name"
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
    name                     = "email"
    required                 = "true"

    string_attribute_constraints {
      max_length = "256"
      min_length = "0"
    }
  }

  schema {
    attribute_data_type      = "String"
    developer_only_attribute = "false"
    mutable                  = "true"
    name                     = "identity_provider"
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
    name                     = "user_guid"
    required                 = "false"

    string_attribute_constraints {
      max_length = "256"
      min_length = "0"
    }
  }

  username_configuration {
    case_sensitive = "false"
  }

  verification_message_template {
    default_email_option = "CONFIRM_WITH_CODE"
  }
}

resource "aws_cognito_user_pool_domain" "main" {
  domain       = "${random_pet.fam_user_pool_name.id}-domain"
  user_pool_id = aws_cognito_user_pool.fam_user_pool.id
}