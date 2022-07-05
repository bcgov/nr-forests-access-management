resource "aws_iam_role_policy" "secretmasterDB_access_policy" {
  name   = "secretmasterDB_access_policy"
  role   = aws_iam_role.flyway_lambda_exec.id
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
        "Resource": "${aws_secretsmanager_secret.secretmasterDB.arn}"
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

data "aws_iam_policy_document" "flyway_lambda_exec_policydoc" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

  }
}

resource "aws_iam_role" "flyway_lambda_exec" {
  name = "flyway_serverless_lambda_role"
  assume_role_policy = data.aws_iam_policy_document.flyway_lambda_exec_policydoc.json
}

resource "aws_lambda_function" "db-migrations" {
  filename      = "db-migrations/lambda/flyway-0.0.4.zip"
  function_name = "lambda-db-migrations"
  role          = aws_iam_role.flyway_lambda_exec.arn
  # has to have the form filename.functionname where filename is the file containing the export
  handler = "index.handler"

  # The filebase64sha256() function is available in Terraform 0.11.12 and later
  # For Terraform 0.11.11 and earlier, use the base64sha256() function and the file() function:
  # source_code_hash = "${base64sha256(file("lambda_function_payload.zip"))}"
  source_code_hash = filebase64sha256("db-migrations/lambda/flyway-0.0.4.zip")

  runtime = "java11"

  vpc_config {
    subnet_ids         = [data.aws_subnet.a.id, data.aws_subnet.b.id]
    security_group_ids = [data.aws_security_group.a.id]
  }

  timeout = 45

  environment {
    variables = {
      DB_SECRET = "${var.db_master_creds_secretname}"
    }
  }

  tags = {
    "managed-by" = "terraform"
  }
}
