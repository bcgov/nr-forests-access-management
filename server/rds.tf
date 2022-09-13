# BEGIN CREATE RANDOM PASSWORD FOR RDS MASTER USER

resource "random_password" "db_password" {
  length           = 16
  special          = true
  override_special = "_%@"
}

resource "aws_secretsmanager_secret" "secretmasterDB" {
   name = var.db_master_creds_secretname
}

resource "aws_secretsmanager_secret_version" "sversion" {
  secret_id = aws_secretsmanager_secret.secretmasterDB.id
  secret_string = <<EOF
   {
    "username": "${var.db_username}",
    "password": "${random_password.db_password.result}"
   }
EOF
}

data "aws_secretsmanager_secret" "secretmasterDB" {
  arn = aws_secretsmanager_secret.secretmasterDB.arn
}

data "aws_secretsmanager_secret_version" "creds" {
  secret_id = data.aws_secretsmanager_secret.secretmasterDB.arn
}

locals {
  db_creds = jsondecode(data.aws_secretsmanager_secret_version.creds.secret_string)
}

# END CREATE RANDOM PASSWORD FOR RDS MASTER USER

# Create RDS database
module "db" {
  source  = "terraform-aws-modules/rds-aurora/aws"
  version = "~> 3.0"

  name           = var.db_cluster_identifier
  engine         = "aurora-postgresql"
  engine_version = "11.9"
  engine_mode    = "serverless"

  vpc_id                 = data.aws_vpc.selected.id
  vpc_security_group_ids = [data.aws_security_group.a.id]
  subnets                = [data.aws_subnet.a.id, data.aws_subnet.b.id]

  allowed_security_groups = [data.aws_security_group.a.id]

  replica_scale_enabled = false
  replica_count         = 0

  storage_encrypted = true
  apply_immediately = true
  # 0 is used to disable enhanced monitoring
  monitoring_interval = 0
  # Remove this to save a final snapshot before database is destroyed
  skip_final_snapshot  = false
  enable_http_endpoint = true

  scaling_configuration = {
    auto_pause               = true
    min_capacity             = 2
    max_capacity             = 2
    seconds_until_auto_pause = 300
    timeout_action           = "ForceApplyCapacityChange"
  }

  create_random_password = false
  username               = local.db_creds.username
  password               = local.db_creds.password
  database_name          = var.db_name

  tags = {
    "managed-by" = "terraform"
  }
  
}

data "aws_rds_cluster" "database" {
  cluster_identifier = var.db_cluster_identifier
  depends_on = [
    module.db
  ]
}

# Begin Create DB Secret for the API database user

resource "random_password" "api_db_password" {
  length           = 16
  special          = true
  override_special = "_%@"
}

resource "aws_secretsmanager_secret" "secret_api_DB" {
   name = var.db_api_creds_secretname
}

resource "aws_secretsmanager_secret_version" "sversion-api" {
  secret_id = aws_secretsmanager_secret.secret_api_DB.id
  secret_string = <<EOF
   {
    "username": "${var.api_db_username}",
    "password": "${random_password.api_db_password.result}"
   }
  EOF
}

# End Create DB Secret for the API database user
