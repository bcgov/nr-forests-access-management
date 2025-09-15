data "aws_secretsmanager_secret" "db_flyway_master_creds" {
  name = aws_secretsmanager_secret.famdb_mastercreds_secret.name
}

data "aws_secretsmanager_secret" "db_flyway_api_creds" {
  name = aws_secretsmanager_secret.famdb_apicreds_secret.name
}

data "aws_secretsmanager_secret_version" "db_flyway_api_creds_current" {
  secret_id = data.aws_secretsmanager_secret.db_flyway_api_creds.id

  depends_on = [
    # Fix race condition
    aws_secretsmanager_secret_version.famdb_apicreds_secret_version
  ]
}

data "aws_secretsmanager_secret" "db_flyway_admin_management_api_creds" {
  name = aws_secretsmanager_secret.famdb_admin_management_apicreds_secret.name
}

data "aws_secretsmanager_secret_version" "db_flyway_admin_management_api_creds_current" {
  secret_id = data.aws_secretsmanager_secret.db_flyway_admin_management_api_creds.id

  depends_on = [
    # Fix race condition
    aws_secretsmanager_secret_version.famdb_admin_management_apicreds_secret_version
  ]
}

data "aws_secretsmanager_secret" "db_flyway_auth_creds" {
  name = aws_secretsmanager_secret.famdb_auth_lambda_creds_secret.name
}

data "aws_secretsmanager_secret_version" "db_flyway_auth_creds_current" {
  secret_id = data.aws_secretsmanager_secret.db_flyway_auth_creds.id

  depends_on = [
    # Fix race condition
    aws_secretsmanager_secret_version.famdb_auth_lambda_creds_secret_version
  ]
}


data "aws_rds_cluster" "flyway_database" {
  cluster_identifier = var.famdb_cluster_name
  depends_on = [
    module.aurora_postgresql_v2
  ]
}

locals {
  flyway_lambda_name = "fam-flyway-lambda-${var.target_env}"
  # S3 bucket nees to be globally unique. This bucket name was conflict with ASEA for LZA, so add licence plate.
  flyway_scripts_bucket_name = "fam-flyway-bucket-${var.licence_plate}-${var.target_env}"
}

# IAM role to allow lambda to run, access secret, and access sql from s3

resource "aws_iam_role_policy" "flyway_access_policy" {
  name   = "${local.flyway_lambda_name}-access-policy"
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
          "s3:GetObject",
          "s3:GetObjectAcl",
          "s3:ListBucket"
        ],
        "Resource": [
          "${aws_s3_bucket.flyway_scripts.arn}",
          "${aws_s3_bucket.flyway_scripts.arn}/*"
        ]
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
  name               = "${local.flyway_lambda_name}-role"
  assume_role_policy = data.aws_iam_policy_document.flyway_exec_policydoc.json
}

resource "aws_lambda_function" "flyway-migrations" {
  filename      = "${path.module}/flyway-all.jar"
  function_name = local.flyway_lambda_name
  role          = aws_iam_role.flyway_exec.arn
  # has to have the form filename.functionname where filename is the file containing the export
  handler = "com.geekoosh.flyway.FlywayHandler::handleRequest"

  # The filebase64sha256() function is available in Terraform 0.11.12 and later
  # For Terraform 0.11.11 and earlier, use the base64sha256() function and the file() function:
  # source_code_hash = "${base64sha256(file("lambda_function_payload.zip"))}"
  source_code_hash = filebase64sha256("${path.module}/flyway-all.jar")

  runtime = "java11"

  vpc_config {
    subnet_ids         = [data.aws_subnet.a_app.id, data.aws_subnet.b_app.id]
    security_group_ids = ["${aws_security_group.fam_app_sg.id}"]
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

# This section writes the flyway scripts to an S3 bucket

resource "aws_s3_bucket" "flyway_scripts" {
  bucket = local.flyway_scripts_bucket_name
}

resource "aws_s3_bucket_policy" "flyway_scripts_policy" {
  bucket = aws_s3_bucket.flyway_scripts.bucket

  policy = jsonencode({
    Version = "2012-10-17"
    Id      = "flyway_scripts_policy"
    Statement = [
      {
        Sid       = "HTTPSOnly"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          "${aws_s3_bucket.flyway_scripts.arn}",
          "${aws_s3_bucket.flyway_scripts.arn}/*",
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      },
    ]
  })
}

locals {
  src_dir = "./sql/"
  files_raw = fileset(local.src_dir, "**")
  files = toset([
    for sqlFile in local.files_raw:
      sqlFile if sqlFile != ".terragrunt-source-manifest" && sqlFile != "assets/.terragrunt-source-manifest"
  ])
}

resource "aws_s3_bucket_public_access_block" "flyway_scripts_public_access_block" {
  bucket = aws_s3_bucket.flyway_scripts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_object" "sql_files" {
  for_each = local.files

  # Create an object from each
  bucket = aws_s3_bucket.flyway_scripts.id
  key    = each.value
  source = "${local.src_dir}/${each.value}"
  etag = filemd5("${local.src_dir}/${each.value}")
  content_type = "text/txt"
}

# Everything below here is for invoking flyway.

resource "aws_db_cluster_snapshot" "fam_pre_flyway_snapshot" {
  db_cluster_identifier          = data.aws_rds_cluster.flyway_database.id
  db_cluster_snapshot_identifier = var.db_cluster_snapshot_identifier
  count                          = var.execute_flyway ? 1 : 0
}

# Need to grab the username and password from the database so they can go into the scripts
locals {
  flyway_db_creds = jsondecode(data.aws_secretsmanager_secret_version.db_flyway_api_creds_current.secret_string)
  flyway_db_admin_management_api_creds = jsondecode(data.aws_secretsmanager_secret_version.db_flyway_admin_management_api_creds_current.secret_string)
  flyway_db_auth_creds = jsondecode(data.aws_secretsmanager_secret_version.db_flyway_auth_creds_current.secret_string)
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
          "api_db_password" : "md5${md5(join("", [local.flyway_db_creds.password, local.flyway_db_creds.username]))}",
          "auth_lambda_db_user" : "${local.flyway_db_auth_creds.username}",
          "auth_lambda_db_password" : "md5${md5(join("", [local.flyway_db_auth_creds.password, local.flyway_db_auth_creds.username]))}",
          "admin_management_api_db_user" : "${local.flyway_db_admin_management_api_creds.username}",
          "admin_management_api_db_password" : "md5${md5(join("", [local.flyway_db_admin_management_api_creds.password, local.flyway_db_admin_management_api_creds.username]))}",
          "client_id_fam_console" : "${aws_cognito_user_pool_client.fam_console_oidc_client.id}",
          "client_id_fom_public" : "nolongerinuse1",
          "client_id_fom_ministry" : "nolongerinuse2",
          "client_id_dev_fom_oidc_client" : "${aws_cognito_user_pool_client.dev_fom_oidc_client.id}",
          "client_id_test_fom_oidc_client" : "${aws_cognito_user_pool_client.test_fom_oidc_client.id}",
          "client_id_prod_fom_oidc_client" : "${aws_cognito_user_pool_client.prod_fom_oidc_client.id}",
          "client_id_dev_spar_oidc_client" : "${aws_cognito_user_pool_client.dev_spar_oidc_client.id}",
          "client_id_test_spar_oidc_client" : "${aws_cognito_user_pool_client.test_spar_oidc_client.id}",
          "client_id_prod_spar_oidc_client" : "${aws_cognito_user_pool_client.prod_spar_oidc_client.id}",
          "client_id_dev_forest_client_oidc_client" : "${aws_cognito_user_pool_client.dev_forest_client_oidc_client.id}",
          "client_id_test_forest_client_oidc_client" : "${aws_cognito_user_pool_client.test_forest_client_oidc_client.id}",
          "client_id_prod_forest_client_oidc_client" : "${aws_cognito_user_pool_client.prod_forest_client_oidc_client.id}",
          "client_id_dev_silva_oidc_client" : "${aws_cognito_user_pool_client.dev_silva_oidc_client.id}",
          "client_id_test_silva_oidc_client" : "${aws_cognito_user_pool_client.test_silva_oidc_client.id}",
          "client_id_prod_silva_oidc_client" : "${aws_cognito_user_pool_client.prod_silva_oidc_client.id}",
          "client_id_dev_apt_oidc_client" : "${aws_cognito_user_pool_client.dev_apt_oidc_client.id}",
          "client_id_test_apt_oidc_client" : "${aws_cognito_user_pool_client.test_apt_oidc_client.id}",
          "client_id_prod_apt_oidc_client" : "${aws_cognito_user_pool_client.prod_apt_oidc_client.id}",
          "client_id_dev_results_exam_oidc_client" : "${aws_cognito_user_pool_client.dev_results_exam_oidc_client.id}",
          "client_id_test_results_exam_oidc_client" : "${aws_cognito_user_pool_client.test_results_exam_oidc_client.id}",
          "client_id_prod_results_exam_oidc_client" : "${aws_cognito_user_pool_client.prod_results_exam_oidc_client.id}",
          "client_id_dev_ilcr_oidc_client" : "${aws_cognito_user_pool_client.dev_ilcr_oidc_client.id}",
          "client_id_test_ilcr_oidc_client" : "${aws_cognito_user_pool_client.test_ilcr_oidc_client.id}",
          "client_id_prod_ilcr_oidc_client" : "${aws_cognito_user_pool_client.prod_ilcr_oidc_client.id}",
          "client_id_dev_waste_plus_oidc_client" : "${aws_cognito_user_pool_client.dev_waste_plus_oidc_client.id}",
          "client_id_test_waste_plus_oidc_client" : "${aws_cognito_user_pool_client.test_waste_plus_oidc_client.id}",
          "client_id_prod_waste_plus_oidc_client" : "${aws_cognito_user_pool_client.prod_waste_plus_oidc_client.id}"
        },
        "target": "latest"
    },
    "dbRequest": {
        "connectionString": "jdbc:postgresql://${data.aws_rds_cluster.flyway_database.endpoint}/${data.aws_rds_cluster.flyway_database.database_name}"
    },
    "s3Request": {
        "bucket": "${aws_s3_bucket.flyway_scripts.bucket}"
    }
  }
  JSON

  # If there is a new flyway that requires Cognito clients (the IDs) to be created, "add the new clients in this block"
  # when BOTH the NEW flyway and the NEW clients need to be applied together.
  # If the new client is already created separately before flyway run, then it can be left out of this block.
  depends_on = [
    aws_db_cluster_snapshot.fam_pre_flyway_snapshot,
    aws_cognito_user_pool_client.fam_console_oidc_client,
    aws_cognito_user_pool_client.dev_fom_oidc_client,
    aws_cognito_user_pool_client.test_fom_oidc_client,
    aws_cognito_user_pool_client.prod_fom_oidc_client,
    aws_cognito_user_pool_client.dev_spar_oidc_client,
    aws_cognito_user_pool_client.test_spar_oidc_client,
    aws_cognito_user_pool_client.prod_spar_oidc_client,
    aws_cognito_user_pool_client.dev_forest_client_oidc_client,
    aws_cognito_user_pool_client.test_forest_client_oidc_client,
    aws_cognito_user_pool_client.prod_forest_client_oidc_client,
    aws_s3_object.sql_files,
  ]

  count = var.execute_flyway ? 1 : 0
}
