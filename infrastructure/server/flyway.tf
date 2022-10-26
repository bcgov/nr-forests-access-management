# Looking up a few things so they can be changed for this file in one place only

data "aws_secretsmanager_secret" "db_flyway_master_creds" {
  name = aws_secretsmanager_secret.famdb_mastercreds_secret.name
}

data "aws_secretsmanager_secret" "db_flyway_api_creds" {
  name = aws_secretsmanager_secret.famdb_apicreds_secret.name
}

data "aws_secretsmanager_secret_version" "db_flyway_api_creds_current" {
  secret_id = data.aws_secretsmanager_secret.db_flyway_api_creds.id

  depends_on = [
    aws_secretsmanager_secret_version.famdb_apicreds_secret_version
  ]
}

data "aws_rds_cluster" "flyway_database" {
  cluster_identifier = var.famdb_cluster_name
  depends_on = [
    module.aurora_postgresql_v2
  ]
}

# Random names to allow multiple instances per workspace

resource "random_pet" "flyway_lambda_name" {
  prefix = "flyway-lambda"
  length = 2
}

# IAM role to allow lambda to run and access secret

resource "aws_iam_role_policy" "flyway_access_policy" {
  name   = "${random_pet.flyway_lambda_name.id}-access-policy"
  role   = aws_iam_role.flyway_exec.id
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
        "Resource": "${data.aws_secretsmanager_secret.db_flyway_master_creds.arn}"
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

data "aws_iam_policy_document" "flyway_exec_policydoc" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "flyway_exec" {
  name               = "${random_pet.flyway_lambda_name.id}-role"
  assume_role_policy = data.aws_iam_policy_document.flyway_exec_policydoc.json
}

resource "aws_lambda_function" "flyway-migrations" {
  filename      = "${path.module}/flyway-all.jar"
  function_name = random_pet.flyway_lambda_name.id
  role          = aws_iam_role.flyway_exec.arn
  # has to have the form filename.functionname where filename is the file containing the export
  handler = "com.geekoosh.flyway.FlywayHandler::handleRequest"

  # The filebase64sha256() function is available in Terraform 0.11.12 and later
  # For Terraform 0.11.11 and earlier, use the base64sha256() function and the file() function:
  # source_code_hash = "${base64sha256(file("lambda_function_payload.zip"))}"
  source_code_hash = filebase64sha256("${path.module}/flyway-all.jar")

  runtime = "java11"

  vpc_config {
    subnet_ids         = [data.aws_subnet.a_data.id, data.aws_subnet.b_data.id]
    security_group_ids = [data.aws_security_group.sg_data.id]
  }

  memory_size = 512
  timeout     = 240

  environment {
    variables = {
      DB_SECRET      = "${data.aws_secretsmanager_secret.db_flyway_master_creds.name}"
      FLYWAY_MIXED   = "false"
      FLYWAY_SCHEMAS = "flyway,app_fam"
    }
  }

  tags = {
    "managed-by" = "terraform"
  }
}

# Everything below here is for invoking flyway. It only happens if there is a push

resource "aws_db_cluster_snapshot" "fam_pre_flyway_snapshot" {
  db_cluster_identifier          = data.aws_rds_cluster.flyway_database.id
  db_cluster_snapshot_identifier = "pre-flyway-${var.github_branch}-${var.github_commit}"
  count                          = var.github_event == "push" ? 1 : 0
}

# Need to grab the username and password from the database so they can go into the scripts

locals {
  flyway_db_creds = jsondecode(data.aws_secretsmanager_secret_version.db_flyway_api_creds_current.secret_string)
}

# Run flyway to update the database

data "aws_lambda_invocation" "invoke_flyway_migration" {
  function_name = aws_lambda_function.flyway-migrations.function_name

  input = <<JSON
  {
    "flywayRequest": {
        "flywayMethod": "MIGRATE",
        "placeholders": {
          "api_db_username" : "${local.flyway_db_creds.username}",
          "api_db_password" : "md5${md5(join("", [local.flyway_db_creds.password, local.flyway_db_creds.username]))}"
        },
        "target": "latest"
    },
    "dbRequest": {
        "connectionString": "jdbc:postgresql://${data.aws_rds_cluster.flyway_database.endpoint}/${data.aws_rds_cluster.flyway_database.database_name}"
    },
    "gitRequest": {
        "gitRepository": "${var.github_repository}",
        "gitBranch": "${var.github_branch}",
        "folders": "server/flyway/sql"
    }
  }
  JSON

  depends_on = [
    aws_db_cluster_snapshot.fam_pre_flyway_snapshot
  ]

  count = var.github_event == "push" ? 1 : 0
}
