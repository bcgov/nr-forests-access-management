# Looking up a few things so they can be changed for this file in one place only

data "aws_secretsmanager_secret" "db_api_creds_secret_kevin" {
  name = aws_secretsmanager_secret.famdb_apicreds_secret.name
}

data "aws_rds_cluster" "api_database_kevin" {
  cluster_identifier = random_pet.famdb_cluster_name.id
  depends_on = [
    module.aurora_postgresql_v2
  ]
}

data "aws_iam_role" "secret_access_role_kevin" {
  name = "${aws_iam_role.fam_api_lambda_exec.name }"
}

data "aws_db_proxy" "api_lambda_db_proxy_kevin" {
  name = aws_db_proxy.famdb_proxy_api.name
}

# Defining new resources

resource "aws_lambda_function" "fam-api_lambda_function" {
  filename      = "fam-ui-api.zip"
  function_name = "fam-api-lambda"
  role          = data.aws_iam_role.secret_access_role_kevin.arn
  handler = "api.app.main.handler"

  source_code_hash = filebase64sha256("fam-ui-api.zip")

  runtime = "python3.8"

  vpc_config {
    security_group_ids = [data.aws_security_group.sg_app.id]
    subnet_ids         = [data.aws_subnet.a_app.id, data.aws_subnet.b_app.id]
  }

  environment {

    variables = {
      DB_SECRET   = "${data.aws_secretsmanager_secret.db_api_creds_secret_kevin.name}"
      PG_DATABASE = "${data.aws_rds_cluster.api_database_kevin.database_name}"
      PG_PORT = "5432"
      PG_HOST = "${data.aws_db_proxy.api_lambda_db_proxy_kevin.endpoint}"
    }

  }

  tags = {
    "managed-by" = "terraform"
  }
}