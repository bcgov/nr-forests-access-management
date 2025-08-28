# Lookup variables outside file

data "aws_lambda_function" "target_lambda" {
  function_name = aws_lambda_function.fam-api-function.function_name
}

# defines the gateway name as the name of the lambda function with
# the text '-gateway' appended to it.

resource "aws_api_gateway_rest_api" "fam_api_gateway_rest_api" {
  name = "${data.aws_lambda_function.target_lambda.function_name}-gateway"
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_resource" "fam_api_gateway_resource" {
  rest_api_id = aws_api_gateway_rest_api.fam_api_gateway_rest_api.id
  parent_id   = aws_api_gateway_rest_api.fam_api_gateway_rest_api.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "fam_api_gateway_method_proxy" {
  rest_api_id   = aws_api_gateway_rest_api.fam_api_gateway_rest_api.id
  resource_id   = aws_api_gateway_resource.fam_api_gateway_resource.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "fam_api_gateway_integration_proxy" {
  rest_api_id = aws_api_gateway_rest_api.fam_api_gateway_rest_api.id
  resource_id = aws_api_gateway_resource.fam_api_gateway_resource.id
  http_method = aws_api_gateway_method.fam_api_gateway_method_proxy.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = data.aws_lambda_function.target_lambda.invoke_arn
}

resource "aws_api_gateway_method" "fam_api_gateway_method_proxy_root" {
  rest_api_id   = aws_api_gateway_rest_api.fam_api_gateway_rest_api.id
  resource_id   = aws_api_gateway_rest_api.fam_api_gateway_rest_api.root_resource_id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "fam_api_gateway_integration_proxy_root" {
  rest_api_id = aws_api_gateway_rest_api.fam_api_gateway_rest_api.id
  resource_id = aws_api_gateway_method.fam_api_gateway_method_proxy_root.resource_id
  http_method = aws_api_gateway_method.fam_api_gateway_method_proxy_root.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = data.aws_lambda_function.target_lambda.invoke_arn
}


resource "aws_api_gateway_deployment" "fam_api_gateway_deployment" {
  depends_on = [
    aws_api_gateway_integration.fam_api_gateway_integration_proxy,
    aws_api_gateway_integration.fam_api_gateway_integration_proxy_root
  ]

  triggers = {
    redeployment = sha1(jsonencode(aws_api_gateway_rest_api.fam_api_gateway_rest_api.id))
  }

  rest_api_id = aws_api_gateway_rest_api.fam_api_gateway_rest_api.id
  stage_name  = var.api_gateway_stage_name  # Terraform warns about using "stage_name" in resource "aws_api_gateway_deployment".
                                            # See https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_deployment
                                            # If possible in the future, use "aws_api_gateway_stage" resource instead. But may face issue about:
                                            # Error: creating API Gateway Stage (v1): ConflictException: Stage already exists.

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_lambda_permission" "fam_api_gateway_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = data.aws_lambda_function.target_lambda.function_name
  principal     = "apigateway.amazonaws.com"

  # The "/*/*" portion grants access from any method on any resource
  # within the API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.fam_api_gateway_rest_api.execution_arn}/*/*"
}

resource "aws_wafv2_web_acl_association" "fam_waf_api_gateway_association" {
  # Normally the "resource_arn" value should be from here: resource_arn = aws_api_gateway_stage.fam_api_gateway_stage.arn
  # But code it with "arn:aws:...." format for now as we currently have problem create "fam_api_gateway_stage" resouce.
  resource_arn = "arn:aws:apigateway:${data.aws_region.current.name}::/restapis/${aws_api_gateway_rest_api.fam_api_gateway_rest_api.id}/stages/${var.api_gateway_stage_name}"
  web_acl_arn  = aws_wafv2_web_acl.fam_waf_api_gateway.arn
  depends_on = [
    aws_wafv2_web_acl.fam_waf_api_gateway
    # aws_api_gateway_stage.fam_api_gateway_stage  # enable this only if in future we could create "_stage" resource.
  ]
}

module "fam_api_cors" {
  source  = "squidfunk/api-gateway-enable-cors/aws"
  version = "0.3.3"

  api_id          = aws_api_gateway_rest_api.fam_api_gateway_rest_api.id
  api_resource_id = aws_api_gateway_resource.fam_api_gateway_resource.id
}
