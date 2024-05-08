# Looking up a few things so they can be changed for this file in one place only

data "aws_secretsmanager_secret" "db_admin_management_api_creds_secret" {
  name = aws_secretsmanager_secret.famdb_admin_management_apicreds_secret.name
}

data "aws_rds_cluster" "admin_management_api_database" {
  cluster_identifier = var.famdb_cluster_name
  depends_on = [
    module.aurora_postgresql_v2
  ]
}

data "aws_db_proxy" "admin_management_api_lambda_db_proxy" {
  name = aws_db_proxy.famdb_proxy_api.name
}

locals {
  admin_management_api_lambda_name = "fam-admin-management-api-lambda-${var.target_env}"
}

resource "aws_iam_role_policy" "fam_admin_management_api_lambda_access_policy" {
  name   = "${local.admin_management_api_lambda_name}-access-policy"
  role   = aws_iam_role.fam_admin_management_api_lambda_exec.id
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
        "Resource": "${data.aws_secretsmanager_secret.db_admin_management_api_creds_secret.arn}"
      },
      {
        "Effect": "Allow",
        "Action": [
          "secretsmanager:DescribeSecret",
          "secretsmanager:GetSecretValue"
        ],
        "Resource": "${data.aws_secretsmanager_secret.fam_oidc_client_id_secret.arn}"
      },
      {
        "Effect": "Allow",
        "Action": [
                "kms:*"
            ],
        "Resource": "${aws_kms_key.bcsc_key.arn}"
      }
    ]
  }
  EOF
}

data "aws_iam_policy_document" "fam_admin_management_api_lambda_exec_policydoc" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "fam_admin_management_api_lambda_exec" {
  name               = "${local.admin_management_api_lambda_name}-role"
  assume_role_policy = data.aws_iam_policy_document.fam_admin_management_api_lambda_exec_policydoc.json
}

# Had to move COGNITO_CLIENT_ID out of ENV and into an AWS Secret because of a
# cycle dependency in the build. That's why it's not here. You still need it
# when running local or in docker.
# Need to supply COGNITO_CLIENT_ID_SECRET_NAME when deploying with terraform

resource "aws_lambda_function" "fam_admin_management_api_function" {
  filename      = "fam-admin-management-api.zip"
  function_name = local.admin_management_api_lambda_name
  role          = aws_iam_role.fam_admin_management_api_lambda_exec.arn
  handler       = "api.app.main.handler"

  source_code_hash = filebase64sha256("fam-admin-management-api.zip")

  runtime = "python3.8"

  vpc_config {
    security_group_ids = ["${aws_security_group.fam_app_sg.id}"]
    subnet_ids         = [data.aws_subnet.a_app.id, data.aws_subnet.b_app.id]
  }

  # Increase memory to avoid thrashing and slowing performance
  # Size is in MB, based on limited testing in dev
  memory_size = 512

  # Increase timeout to 15 seconds to avoid failures due to slow starts or slow queries.
  # We have seen transactions taking 7+ seconds in dev.
  timeout = 15

  environment {

    variables = {
      DB_SECRET                = "${data.aws_secretsmanager_secret.db_admin_management_api_creds_secret.name}"
      PG_DATABASE              = "${data.aws_rds_cluster.admin_management_api_database.database_name}"
      PG_PORT                  = "5432"
      PG_HOST                  = "${data.aws_db_proxy.admin_management_api_lambda_db_proxy.endpoint}"
      COGNITO_REGION           = "${data.aws_region.current.name}"
      COGNITO_USER_POOL_ID     = "${aws_cognito_user_pool.fam_user_pool.id}"
      COGNITO_USER_POOL_DOMAIN = "${var.fam_user_pool_domain_name}"
      COGNITO_CLIENT_ID_SECRET = "${data.aws_secretsmanager_secret.fam_oidc_client_id_secret.name}"

      API_GATEWAY_STAGE_NAME = "${var.api_gateway_stage_name}"
      COGNITO_CLIENT_ID        = "3hv7q2mct0okt12m5i3p5v4phu"

      ALLOW_ORIGIN = "${var.front_end_redirect_path}"

      FC_API_TOKEN = "${var.forest_client_api_api_key}"
      FC_API_BASE_URL = "${var.forest_client_api_base_url}"

      IDIM_PROXY_BASE_URL = "${var.idim_proxy_api_base_url}"
      IDIM_PROXY_API_KEY = "${var.idim_proxy_api_api_key}"
    }

  }

  tags = {
    "managed-by" = "terraform"
  }
}
