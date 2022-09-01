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
      PG_HOST = "${aws_db_proxy.example.endpoint}"
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
          "${aws_secretsmanager_secret.secret_api_DB.arn}"
        ]
      }
    ]
  }
  EOF
}

# module "rds_proxy" {
#   source = "terraform-aws-modules/rds-proxy/aws"

#   role_arn = aws_iam_role.api_user_rds_proxy_secret_access_role.arn

#   name                   = "fam-api-rds-proxy"
#   vpc_security_group_ids = [data.aws_security_group.a.id]
#   vpc_subnet_ids         = [data.aws_subnet.a.id, data.aws_subnet.b.id]
#   manage_log_group       = false
#   create_iam_policy      = true
#   create_iam_role        = true
#   iam_auth = "DISABLED"

#   secrets = {
#     "api_user" = {
#       description = aws_secretsmanager_secret.secret_api_DB.description
#       arn         = aws_secretsmanager_secret.secret_api_DB.arn
#       kms_key_id  = aws_secretsmanager_secret.secret_api_DB.kms_key_id
#     }
#   }

#   engine_family = "POSTGRESQL"
#   debug_logging = true

#   # Target Aurora cluster
#   target_db_cluster     = true
#   db_cluster_identifier = data.aws_rds_cluster.database.id

#   tags = {
#     "managed-by" = "terraform"
#   }
# }

resource "aws_db_proxy" "example" {
  name                   = "example"
  debug_logging          = false
  engine_family          = "POSTGRESQL"
  idle_client_timeout    = 1800
  require_tls            = true
  role_arn               = aws_iam_role.api_user_rds_proxy_secret_access_role.arn
  vpc_security_group_ids = [data.aws_security_group.a.id]
  vpc_subnet_ids         = [data.aws_subnet.a.id, data.aws_subnet.b.id]

  auth {
    auth_scheme = "SECRETS"
    description = "example"
    iam_auth    = "DISABLED"
    secret_arn  = aws_secretsmanager_secret.secret_api_DB.arn
  }

  tags = {
    Name = "example"
    Key  = "value"
  }
}

resource "aws_db_proxy_default_target_group" "example" {
  db_proxy_name = aws_db_proxy.example.name

  connection_pool_config {
    connection_borrow_timeout    = 120
    init_query                   = "SET x=1, y=2"
    max_connections_percent      = 100
    max_idle_connections_percent = 50
    session_pinning_filters      = []
  }
}

resource "aws_db_proxy_target" "example" {
  db_cluster_identifier = data.aws_rds_cluster.database.id
  db_proxy_name          = aws_db_proxy.example.name
  target_group_name      = aws_db_proxy_default_target_group.example.name
}







