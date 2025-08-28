resource "aws_api_gateway_rest_api" "admin_management_api_gateway_rest_api" {
  name = "${aws_lambda_function.fam_admin_management_api_function.function_name}-gateway"
  description = "Proxy API Gateway to handle request to fam-admin-management-api-lambda."
  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = {
    Name = "fam_admin_api_gateway"
    managed-by = "terraform"
  }
}

resource "aws_api_gateway_resource" "admin_management_api_gateway_resource_proxy" {
  rest_api_id = aws_api_gateway_rest_api.admin_management_api_gateway_rest_api.id
  parent_id   = aws_api_gateway_rest_api.admin_management_api_gateway_rest_api.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "admin_management_api_gateway_method_proxy" {
  rest_api_id   = aws_api_gateway_rest_api.admin_management_api_gateway_rest_api.id
  resource_id   = aws_api_gateway_resource.admin_management_api_gateway_resource_proxy.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "admin_management_api_gateway_integration_proxy" {
  rest_api_id = aws_api_gateway_rest_api.admin_management_api_gateway_rest_api.id
  resource_id = aws_api_gateway_resource.admin_management_api_gateway_resource_proxy.id
  http_method = aws_api_gateway_method.admin_management_api_gateway_method_proxy.http_method

  # "...specifying how API Gateway will interact with the back end."
  # Required if type is AWS_PROXY (and some other types).
  # Lambda function can only be invoked via POST.
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.fam_admin_management_api_function.invoke_arn

  depends_on = [
    aws_api_gateway_method.admin_management_api_gateway_method_proxy,
    aws_lambda_function.fam_admin_management_api_function
  ]
}

resource "aws_api_gateway_deployment" "admin_management_api_gateway_deployment" {
  rest_api_id = aws_api_gateway_rest_api.admin_management_api_gateway_rest_api.id

  depends_on = [
    aws_api_gateway_integration.admin_management_api_gateway_integration_proxy
  ]

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.admin_management_api_gateway_resource_proxy.id,
      aws_api_gateway_method.admin_management_api_gateway_method_proxy.id,
      aws_api_gateway_integration.admin_management_api_gateway_integration_proxy.id
    ]))
    # https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_deployment mentioned
    # using whole resouce with filesha1() that may be consider in the future.
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "admin_management_api_gateway_stage" {
  deployment_id = aws_api_gateway_deployment.admin_management_api_gateway_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.admin_management_api_gateway_rest_api.id
  stage_name    = "v1"

  tags = {
    managed-by = "terraform"
  }
}

resource "aws_lambda_permission" "admin_management_api_lambda_permission" {
  statement_id  = "AllowExecutionFromAdminManagementAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fam_admin_management_api_function.function_name
  principal     = "apigateway.amazonaws.com"

  # The "/*/*" portion grants access from any method on any resource
  # within the API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.admin_management_api_gateway_rest_api.execution_arn}/*/*"
}

resource "aws_wafv2_web_acl_association" "waf_admin_management_api_gateway_association" {
  resource_arn = aws_api_gateway_stage.admin_management_api_gateway_stage.arn
  web_acl_arn  = aws_wafv2_web_acl.fam_waf_api_gateway.arn
  depends_on = [
    aws_wafv2_web_acl.fam_waf_api_gateway,
    aws_api_gateway_stage.admin_management_api_gateway_stage
  ]
}

module "admin_management_api_cors" {
  source  = "squidfunk/api-gateway-enable-cors/aws"
  version = "0.3.3"

  api_id          = aws_api_gateway_rest_api.admin_management_api_gateway_rest_api.id
  api_resource_id = aws_api_gateway_resource.admin_management_api_gateway_resource_proxy.id
}
