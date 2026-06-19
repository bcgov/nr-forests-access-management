
resource "aws_cognito_user_pool_client" "fam_service_clients" {
  for_each = local.service_app_envs

  name = "svc-${each.value.app_name}-${each.value.env}"
  # example: svc-fspts-dev

  user_pool_id = aws_cognito_user_pool.fam_user_pool.id

  # Generate a client secret.
  generate_secret = true

  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows = ["client_credentials"]

  allowed_oauth_scopes = [
    for scope in each.value.scopes :
    "${aws_cognito_resource_server.fam_api_resource_server.identifier}/${scope}"
  ]

  access_token_validity = 60 # in minutes
  token_validity_units {
    access_token  = "minutes"
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_cognito_resource_server.fam_api_resource_server
  ]
}

locals {
  environments = ["dev", "test", "prod"]

  # the apps collection; but do not use this directly for creating clients.
  # see below service_app_envs
  service_apps = {
    fspts = {
      # scope should be defined and available in service_account_scopes variable.
      scopes           = ["idim.search.read"]
    }

    # Add more service app below.

  }

  # use this for creating clients for each service app in each environment, e.g. fspts-dev, fspts-test, fspts-prod
  service_app_envs = {
    for pair in flatten([
      for app_name, app in local.service_apps : [
        for env in local.environments : {
          key = "${app_name}-${env}"
          app_name = app_name
          env = env
          scopes = app.scopes
        }
      ]
    ]) : pair.key => pair
  }
}