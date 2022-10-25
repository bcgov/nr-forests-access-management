# Looking up a few things so they can be changed for this file in one place only

data "aws_secretsmanager_secret" "db_auth_creds_secret" {
  name = aws_secretsmanager_secret.famdb_apicreds_secret.name
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

# Random names to allow multiple instances per workspace

resource "random_pet" "auth_lambda_name" {
  prefix = "fam-auth-lambda"
  length = 2
}


resource "aws_iam_role_policy" "fam_auth_lambda_access_policy" {
  name   = "${random_pet.auth_lambda_name.id}-access-policy"
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
        "Resource": "${data.aws_secretsmanager_secret.db_auth_creds_secret.arn}"
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
  name               = "${random_pet.auth_lambda_name.id}-role"
  assume_role_policy = data.aws_iam_policy_document.fam_auth_lambda_exec_policydoc.json
}

resource "aws_lambda_function" "fam-auth-function" {
  filename      = "fam_auth_function.zip"
  function_name = random_pet.auth_lambda_name.id
  role          = aws_iam_role.fam_api_lambda_exec.arn
  handler       = "lambda_function.lambda_handler"

  source_code_hash = filebase64sha256("fam_auth_function.zip")

  runtime = "python3.8"

  vpc_config {
    security_group_ids = [data.aws_security_group.sg_app.id]
    subnet_ids         = [data.aws_subnet.a_app.id, data.aws_subnet.b_app.id]
  }



  environment {

    variables = {
      DB_SECRET   = "${data.aws_secretsmanager_secret.db_api_creds_secret.name}"
      PG_DATABASE = "${data.aws_rds_cluster.api_database.database_name}"
      PG_PORT = "5432"
      PG_HOST = "${data.aws_db_proxy.api_lambda_db_proxy.endpoint}"
    }

  }

  tags = {
    "managed-by" = "terraform"
  }
}

resource "aws_lambda_permission" "allow_cognito_invoke_trigger" {
  statement_id  = "${random_pet.auth_lambda_name.id}-allowCognito"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.fam-auth-function.function_name
  principal     = "cognito-idp.amazonaws.com"
  source_arn    = aws_cognito_user_pool.fam_user_pool.arn
}
