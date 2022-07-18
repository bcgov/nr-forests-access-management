resource "aws_iam_role_policy" "flyway_lambda_access_policy" {
  name   = "flyway_lambda_access_policy"
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
  filename      = "${path.module}/flyway/flyway-all.jar"
  function_name = "lambda-db-migrations"
  role          = aws_iam_role.flyway_lambda_exec.arn
  # has to have the form filename.functionname where filename is the file containing the export
  handler = "com.geekoosh.flyway.FlywayHandler::handleRequest"

  # The filebase64sha256() function is available in Terraform 0.11.12 and later
  # For Terraform 0.11.11 and earlier, use the base64sha256() function and the file() function:
  # source_code_hash = "${base64sha256(file("lambda_function_payload.zip"))}"
  source_code_hash = filebase64sha256("${path.module}/flyway/flyway-all.jar")

  runtime = "java11"

  vpc_config {
    subnet_ids         = [data.aws_subnet.a.id, data.aws_subnet.b.id]
    security_group_ids = [data.aws_security_group.a.id]
  }

  memory_size = 512
  timeout = 240

  environment {
    variables = {
      DB_SECRET = "${var.db_master_creds_secretname}"
      FLYWAY_MIXED = "false"
      FLYWAY_SCHEMAS = "flyway,app_fam"
    }
  }

  tags = {
    "managed-by" = "terraform"
  }
}

# Everything below here is for invoking flyway. It only happens if there is a push

# Need to get the connection string to the Aurora instance

data "aws_rds_cluster" "database" {
  cluster_identifier = var.db_cluster_identifier
}

resource "aws_db_cluster_snapshot" "fam_snapshot" {
  db_cluster_identifier          = data.aws_rds_cluster.database[count.index].id
  db_cluster_snapshot_identifier = "pipeline-${var.github_branch}-${var.github_commit}"
  count = var.github_event == "push" ? 1 : 0
}

# Need to grab the username and password from the database so they can go into the scripts

data "aws_secretsmanager_secret" "db_api_creds" {
  name = var.db_api_creds_secretname
}

data "aws_secretsmanager_secret_version" "api_current" {
  secret_id = data.aws_secretsmanager_secret.db_api_creds.id
}

locals {
  api_db_creds = jsondecode(data.aws_secretsmanager_secret_version.api_current.secret_string)
}

# Run flyway to update the database

data "aws_lambda_invocation" "invoke_flyway" {
  function_name = "lambda-db-migrations"

  input = <<JSON
  {
    "flywayRequest": {
        "flywayMethod": "MIGRATE",
        "placeholders": {
          "api_db_username" : "${local.api_db_creds.username}",
          "api_db_password" : "md5${md5(join("", [local.api_db_creds.password, local.api_db_creds.username]))}"
        },
        "target": "latest"
    },
    "dbRequest": {
        "connectionString": "jdbc:postgresql://${data.aws_rds_cluster.database.endpoint}/${var.db_name}"
    },
    "gitRequest": {
        "gitRepository": "${var.github_repository}",
        "gitBranch": "${var.github_branch}",
        "folders": "server/flyway/sql"
    }
  }
  JSON

  depends_on = [
    aws_db_cluster_snapshot.fam_snapshot
  ]

  count = var.github_event == "push" ? 1 : 0
}