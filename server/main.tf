terraform {
  backend "remote" {}
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.14.0"
    }
  }
}


provider "aws" {
  region = var.aws_region
  assume_role {
    role_arn = "arn:aws:iam::${var.target_aws_account_id}:role/BCGOV_${var.target_env}_Automation_Admin_Role"
  }
}


resource "random_pet" "lambda_bucket_name" {
  prefix = "greetings-lambda"
  length = 4
}

resource "aws_s3_bucket" "lambda_bucket" {
  bucket        = random_pet.lambda_bucket_name.id
  # acl           = "private"
  force_destroy = true
}

resource "random_pet" "upload_bucket_name" {
  prefix = "upload-bucket"
  length = 2
}

resource "aws_s3_bucket" "upload_bucket" {
  bucket        = random_pet.upload_bucket_name.id
  # acl           = "private"
  force_destroy = true
}


data "archive_file" "lambda_greetings_server" {
  type        = "zip"
  source_dir  = "${path.module}/lambda"
  output_path = "${path.module}/greetings-server.zip"
}

resource "aws_s3_bucket_object" "lambda_greetings_server" {
  bucket = aws_s3_bucket.lambda_bucket.id   #argument deprecated
  key    = "greetings-server.zip"
  source = data.archive_file.lambda_greetings_server.output_path
  etag   = filemd5(data.archive_file.lambda_greetings_server.output_path)
}

resource "random_pet" "DB_NAME" {
  prefix = "ssp-greetings"
  length = 2
}


resource "aws_dynamodb_table" "ssp-greetings" {
  name      = random_pet.DB_NAME.id
  hash_key  = "pid"
  range_key = "id"

  billing_mode   = "PAY_PER_REQUEST"
  # read_capacity  = 5
  # write_capacity = 5
  attribute {
    name = "pid"
    type = "S"
  }
  attribute {
    name = "id"
    type = "S"
  }
}






resource "aws_iam_role_policy" "lambda_policy" {
  name   = "lambda_policy"
  role   = aws_iam_role.lambda_exec.id
  policy = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
          "Effect": "Allow",
          "Action": [
              "dynamodb:BatchGet*",
              "dynamodb:DescribeStream",
              "dynamodb:DescribeTable",
              "dynamodb:Get*",
              "dynamodb:Query",
              "dynamodb:Scan",
              "dynamodb:BatchWrite*",
              "dynamodb:CreateTable",
              "dynamodb:Delete*",
              "dynamodb:Update*",
              "dynamodb:PutItem"
          ],
          "Resource": "${aws_dynamodb_table.ssp-greetings.arn}"
        },
        {
          "Effect": "Allow",
           "Action": [
                  "logs:CreateLogGroup",
                  "logs:CreateLogStream",
                   "kms:*",
                  "logs:PutLogEvents",
                  "logs:DescribeLogStreams"
              ],
          "Resource": "*"
      },
       {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:PutBucketCORS"
            ],
            "Resource": [
                "${aws_s3_bucket.upload_bucket.arn}",
                "${aws_s3_bucket.upload_bucket.arn}/*"
            ]
        },
        {
            "Sid": "VisualEditor2",
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:PutBucketCORS"
            ],
            "Resource": [
                "arn:aws:s3:::api-testing-bucket-kiran",
                "arn:aws:s3:::api-testing-bucket-kiran/*"
            ]
        }
    ]
  }
  EOF
}


data "aws_iam_policy_document" "lambda_exec_policydoc" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

  }
}

resource "aws_iam_role" "lambda_exec" {
  name = "serverless_lambda"


  assume_role_policy = data.aws_iam_policy_document.lambda_exec_policydoc.json
}

resource "aws_lambda_function" "greetings_server_lambda" {
  function_name = "greetings_server_fn"

  s3_bucket = aws_s3_bucket.lambda_bucket.id
  s3_key    = aws_s3_bucket_object.lambda_greetings_server.key

  runtime = "nodejs12.x"
  handler = "./lambda.handler"

  source_code_hash = data.archive_file.lambda_greetings_server.output_base64sha256

  role = aws_iam_role.lambda_exec.arn
  environment {
    variables = {
      bucketName = aws_s3_bucket.upload_bucket.id
      DB_NAME    = random_pet.DB_NAME.id
    }
  }

}


resource "aws_api_gateway_rest_api" "apiLambda" {
  name = "myAPI"
}



resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.apiLambda.id
  parent_id   = aws_api_gateway_rest_api.apiLambda.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "proxyMethod" {
  rest_api_id   = aws_api_gateway_rest_api.apiLambda.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = aws_api_gateway_rest_api.apiLambda.id
  resource_id = aws_api_gateway_method.proxyMethod.resource_id
  http_method = aws_api_gateway_method.proxyMethod.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.greetings_server_lambda.invoke_arn
}




resource "aws_api_gateway_method" "proxy_root" {
  rest_api_id   = aws_api_gateway_rest_api.apiLambda.id
  resource_id   = aws_api_gateway_rest_api.apiLambda.root_resource_id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda_root" {
  rest_api_id = aws_api_gateway_rest_api.apiLambda.id
  resource_id = aws_api_gateway_method.proxy_root.resource_id
  http_method = aws_api_gateway_method.proxy_root.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.greetings_server_lambda.invoke_arn
}


resource "aws_api_gateway_deployment" "apideploy" {
  depends_on = [
    aws_api_gateway_integration.lambda,
    aws_api_gateway_integration.lambda_root,
  ]

  rest_api_id = aws_api_gateway_rest_api.apiLambda.id
  stage_name  = "test"
}


resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.greetings_server_lambda.function_name
  principal     = "apigateway.amazonaws.com"

  # The "/*/*" portion grants access from any method on any resource
  # within the API Gateway REST API.
  source_arn = "${aws_api_gateway_rest_api.apiLambda.execution_arn}/*/*"
}


module "cors" {
  source  = "squidfunk/api-gateway-enable-cors/aws"
  version = "0.3.3"

  api_id          = aws_api_gateway_rest_api.apiLambda.id
  api_resource_id = aws_api_gateway_resource.proxy.id


}

# All the following added to get RDS to work

data "aws_vpc" "selected" {
  state = "available"
}

variable "subnet_a" {
  description = "Value of the name tag for the subnet in AZ a"
  default     = "Data_Dev_aza_net"
}

variable "subnet_b" {
  description = "Value of the name tag for the subnet in AZ b"
  default     = "Data_Dev_azb_net"
}

data "aws_subnet" "a" {
  filter {
    name   = "tag:Name"
    values = [var.subnet_a]
  }
}

data "aws_subnet" "b" {
  filter {
    name   = "tag:Name"
    values = [var.subnet_b]
  }
}

resource "aws_security_group" "rds_sg" {
  name        = "rds_sg"
  description = "Security group for AWS lambda and AWS RDS connection"
  vpc_id      = data.aws_vpc.selected.id
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["127.0.0.1/32"]
    self        = true
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# this modules documented outputs all need a prefix of this_
module "db" {
  source  = "terraform-aws-modules/rds-aurora/aws"
  version = "~> 3.0"

  name           = "aurora-db-postgres"
  engine         = "aurora-postgresql"
  engine_version = "11.9"
  engine_mode    = "serverless"

  vpc_id                 = data.aws_vpc.selected.id
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  subnets                = [data.aws_subnet.a.id, data.aws_subnet.b.id]

  allowed_security_groups = [aws_security_group.rds_sg.id]

  replica_scale_enabled = false
  replica_count         = 0

  storage_encrypted = true
  apply_immediately = true
  # 0 is used to disable enhanced monitoring
  monitoring_interval = 0
  # Remove this to save a final snapshot before database is destroyed
  skip_final_snapshot  = false
  enable_http_endpoint = true

  scaling_configuration = {
    auto_pause               = true
    min_capacity             = 2
    max_capacity             = 2
    seconds_until_auto_pause = 300
    timeout_action           = "ForceApplyCapacityChange"
  }

  # create_random_password = false
  # username               = var.db_username
  # password               = random_password.db_password.result
  # database_name          = var.db_name
  

  tags = {
    "managed-by" = "terraform"
  }
  
}
