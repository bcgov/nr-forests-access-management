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
        "Resource": "${aws_secretsmanager_secret.secret_api_DB.arn}"
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

resource "aws_lambda_function" "fam-api" {
  filename      = "fam-api.zip"
  function_name = "fam-api"
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
      PG_DATABASE = "${var.db_name}"
      PG_PORT = "${data.aws_rds_cluster.database.port}"
      PG_HOST = "${data.aws_rds_cluster.database.endpoint}"
    }

  }

  tags = {
    "managed-by" = "terraform"
  }
}

data "aws_iam_policy_document" "api_user_rds_proxy_secret_access_policydoc" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["rds.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "api_user_rds_proxy_secret_access_role" {
  name = "api_user_rds_proxy_secret_access_role"
  assume_role_policy = data.aws_iam_policy_document.api_user_rds_proxy_secret_access_policydoc.json
}

resource "aws_iam_role_policy" "api_user_rds_proxy_secret_access_policy" {
  name   = "api_user_rds_proxy_secret_access_policy"
  role   = aws_iam_role.api_user_rds_proxy_secret_access_role.id
  policy = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "secretsmanager:GetRandomPassword",
          "secretsmanager:ListSecrets"
        ],
        "Resource": "*"
      },
      {
        "Effect": "Allow",
        "Action": [
          "secretsmanager:GetResourcePolicy",
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "secretsmanager:ListSecretVersionIds"
        ],
        "Resource": [
          "arn:aws:secretsmanager:ca-central-1:521834415778:secret:tmpDBSecret-r8DW39"
        ]
      }
    ]
  }
  EOF
}