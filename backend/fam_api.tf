resource "aws_iam_role_policy" "fam-api_lambda_access_policy" {
  name   = "fam-api_lambda_access_policy"
  role   = aws_iam_role.fam-api_lambda_exec.id
  policy = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "secretsmanager:DescribeSecret",
          "secretsmanager:GetSecretValue"
        ],
        "Resource": "${aws_secretsmanager_secret.secret_api_DB.arn}"
      },
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

data "aws_iam_policy_document" "fam-api_lambda_exec_policydoc" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "fam-api_lambda_exec" {
  name = "fam-api_serverless_lambda_role"
  assume_role_policy = data.aws_iam_policy_document.fam-api_lambda_exec_policydoc.json
}
resource "aws_lambda_function" "fam-api-mvp" {
  filename      = "fam-api.zip"
  function_name = "fam-api-mvp"
  role          = aws_iam_role.fam-api_lambda_exec.arn
  handler = "app.main.handler"

  source_code_hash = filebase64sha256("fam-api.zip")

  runtime = "python3.8"

  vpc_config {
    subnet_ids         = [data.aws_subnet.a.id, data.aws_subnet.b.id]
    security_group_ids = [data.aws_security_group.a.id]
  }

  environment {
      variables = {
        DB_SECRET = "${var.db_api_creds_secretname}"
      }
    }

  tags = {
    "managed-by" = "terraform"
  }
}