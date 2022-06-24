resource "aws_lambda_function" "db-migrations" {
  filename      = "lambda-db-migrations.zip"
  function_name = "lambda-db-migrations"
  role          = aws_iam_role.lambda_exec.arn
  # has to have the form filename.functionname where filename is the file containing the export
  handler = "index.handler"

  # The filebase64sha256() function is available in Terraform 0.11.12 and later
  # For Terraform 0.11.11 and earlier, use the base64sha256() function and the file() function:
  # source_code_hash = "${base64sha256(file("lambda_function_payload.zip"))}"
  source_code_hash = filebase64sha256("db-migrations/lambda/flyway-0.0.4.zip")

  runtime = "java11"

  vpc_config {
    subnet_ids         = [data.aws_subnet.a.id, data.aws_subnet.b.id]
    security_group_ids = [data.aws_security_group.a.id]
  }

  timeout = 45

  tags = {
    "managed-by" = "terraform"
  }
}
