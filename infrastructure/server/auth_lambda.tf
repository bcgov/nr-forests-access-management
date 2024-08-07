# Looking up a few things so they can be changed for this file in one place only

data "aws_secretsmanager_secret" "db_auth_creds_secret" {
  name = aws_secretsmanager_secret.famdb_auth_lambda_creds_secret.name
}

data "aws_rds_cluster" "auth_database" {
  cluster_identifier = var.famdb_cluster_name
  depends_on = [
    module.aurora_postgresql_v2
  ]
}

data "aws_db_proxy" "auth_lambda_db_proxy" {
  name = aws_db_proxy.famdb_proxy_api.name
}

locals {
  auth_lambda_name = "fam-auth-lambda-${var.target_env}"
}

resource "aws_iam_role_policy" "fam_auth_lambda_access_policy" {
  name   = "${local.auth_lambda_name}-access-policy"
  role   = aws_iam_role.fam_auth_lambda_exec.id
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
      },
      {
        "Effect": "Allow",
        "Action": [
          "secretsmanager:DescribeSecret",
          "secretsmanager:GetSecretValue"
        ],
        "Resource": "${aws_secretsmanager_secret.famdb_auth_lambda_creds_secret.arn}"
      }
    ]
  }
  EOF
}

data "aws_iam_policy_document" "fam_auth_lambda_exec_policydoc" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "fam_auth_lambda_exec" {
  name               = "${local.auth_lambda_name}-role"
  assume_role_policy = data.aws_iam_policy_document.fam_auth_lambda_exec_policydoc.json
}

resource "aws_lambda_function" "fam-auth-function" {
  filename      = "fam_auth_function.zip"
  function_name = local.auth_lambda_name
  role          = aws_iam_role.fam_auth_lambda_exec.arn
  handler       = "lambda_function.lambda_handler"

  source_code_hash = filebase64sha256("fam_auth_function.zip")

  runtime = "python3.12"

  vpc_config {
    security_group_ids = ["${aws_security_group.fam_app_sg.id}"]
    subnet_ids         = [data.aws_subnet.a_app.id, data.aws_subnet.b_app.id]
  }

  # Increase memory to avoid thrashing and slowing performance
  # Size is in MB. No testing done to confirm what memory limit is best.
  memory_size = 256

  # Increase timeout to 15 seconds avoid failures due to slow starts or slow queries.
  timeout = 15

  environment {

    variables = {
      DB_SECRET   = "${data.aws_secretsmanager_secret.db_auth_creds_secret.name}"
      PG_DATABASE = "${data.aws_rds_cluster.api_database.database_name}"
      PG_PORT     = "5432"
      PG_HOST     = "${data.aws_db_proxy.api_lambda_db_proxy.endpoint}"
    }

  }

  tags = {
    "managed-by" = "terraform"
  }
}

resource "aws_lambda_permission" "allow_cognito_invoke_trigger" {
  statement_id  = "${local.auth_lambda_name}-allowCognito"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fam-auth-function.function_name
  principal     = "cognito-idp.amazonaws.com"
  source_arn    = aws_cognito_user_pool.fam_user_pool.arn
}
