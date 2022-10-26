output "VUE_APP_API_GW_BASE_URL" {
  description = "Base URL for API Gateway stage."
  value       = aws_api_gateway_deployment.fam_api_gateway_deployment.invoke_url
}