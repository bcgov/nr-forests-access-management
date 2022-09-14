resource "aws_lambda_function" "fam-api_kevin" {
  filename      = "fam-ui-api.zip"
  function_name = "fam-api-kevin"
  role          = aws_iam_role.fam-api_lambda_exec.arn
  handler = "api.app.main.handler"

  source_code_hash = filebase64sha256("fam-ui-api.zip")

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