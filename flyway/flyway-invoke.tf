terraform {
  backend "remote" {}
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.14.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  assume_role {
    role_arn = "arn:aws:iam::${var.target_aws_account_id}:role/BCGOV_${var.target_env}_Automation_Admin_Role"
  }
}

# Need to get the connection string to the Aurora instance

data "aws_rds_cluster" "database" {
  cluster_identifier = var.db_cluster_identifier
}

resource "aws_db_cluster_snapshot" "fam_snapshot" {
  db_cluster_identifier          = data.aws_rds_cluster.database.id
  db_cluster_snapshot_identifier = "pipeline-${var.github_branch}-${var.github_commit}"
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
        "folders": "flyway/sql"
    }
  }
  JSON

  depends_on = [
    aws_db_cluster_snapshot.fam_snapshot
  ]

}

output "db_migrations_result" {
  value = jsondecode(data.aws_lambda_invocation.invoke_flyway.result)
}



