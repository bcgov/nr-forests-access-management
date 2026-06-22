
variable "service_account_scopes" {
  type = map(object({
    description = string
  }))

  # available scopes for service accounts, to be used in the aws_cognito_resource_server resource
  default = {
    "User.read" = {
      description = "Allows read access for User data."
    }
  }
}

resource "aws_cognito_resource_server" "fam_api_resource_server" {
  user_pool_id = aws_cognito_user_pool.fam_user_pool.id
  identifier   = "fam-api"
  name         = "fam-api"

  # Dynamically create scopes based on the service_account_scopes variable
  dynamic "scope" {
    for_each = var.service_account_scopes
    content {
      scope_name        = scope.key
      scope_description = scope.value.description
    }
  }

}