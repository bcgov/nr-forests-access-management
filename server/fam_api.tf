resource "aws_iam_role_policy" "api_lambda_access_policy" {
  name   = "api_lambda_access_policy"
  role   = aws_iam_role.api_lambda_exec.id
  policy = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents",
            "ec2:CreateNetworkInterface",
            "ec2:DescribeNetworkInterfaces",
            "ec2:DeleteNetworkInterface",
            "ec2:AssignPrivateIpAddresses",
            "ec2:UnassignPrivateIpAddresses"
        ],
        "Resource": "*"
      }
    ]
  }
  EOF
}

data "aws_iam_policy_document" "api_lambda_exec_policydoc" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "api_lambda_exec" {
  name = "api_serverless_lambda_role"
  assume_role_policy = data.aws_iam_policy_document.api_lambda_exec_policydoc.json
}

resource "aws_lambda_function" "api" {
  filename      = "api.zip"
  function_name = "api"
  role          = aws_iam_role.api_lambda_exec.arn
  handler = "app.main.handler"

  # source_code_hash = filebase64sha256("/home/runner/work/nr-forests-access-management/nr-forests-access-management/api.zip")

  runtime = "python3.8"

  vpc_config {
    subnet_ids         = [data.aws_subnet.a.id, data.aws_subnet.b.id]
    security_group_ids = [data.aws_security_group.a.id]
  }

  tags = {
    "managed-by" = "terraform"
  }
}






