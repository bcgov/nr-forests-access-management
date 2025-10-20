output "fam_admin_management_api_base_url" {
  description = "Base URL for Admin Management API Gateway."
  value       = aws_api_gateway_stage.admin_management_api_gateway_stage.invoke_url
}

output "fam_api_base_url" {
  description = "Base URL for API Gateway stage."
  value       = aws_api_gateway_deployment.fam_api_gateway_deployment.invoke_url
}

data "aws_region" "current" {}

output "fam_cognito_region" {
  description = "Region name for Cognito for front end connection"
  value       = data.aws_region.current.name
}

output "fam_user_pool_id" {
  description = "The ID of the Cognito user pool for front end connection"
  value       = aws_cognito_user_pool.fam_user_pool.id
}

output "fam_console_web_client_id" {
  description = "Web client ID for the FAM OIDC client for front end connection"
  value       = aws_cognito_user_pool_client.fam_console_oidc_client.id
}

output "fam_cognito_domain" {
  description = "Domain associated with the Cognito user pool for front end connection"
  value       = aws_cognito_user_pool_domain.main.domain
}

output "frontend_logout_chain_url" {
  description = "Url of Siteminder and Keycloak logout chain for FAM frontend"
  value = var.target_env == "prod" ? var.cognito_app_client_logout_chain_url.prod : var.cognito_app_client_logout_chain_url.test
}

output "front_end_redirect_base_url" {
  description = "Frontend CloudFront base url"
  value = var.front_end_redirect_path
}

output "target_env" {
  description = "dev, test, or prod in AWS"
  value = var.target_env
}

output "fam_console_idp_name" {
  description = "Identifies which version of IDIR to use (DEV, TEST, or PROD)"
  value = var.fam_console_idp_name
}

output "fam_console_idp_name_bceid" {
  description = "Identifies which version of BUSINESS BCEID to use (DEV, TEST, or PROD)"
  value = var.fam_console_idp_name_bceid
}