data "aws_kms_alias" "rds_key" {
  name = "alias/aws/rds"
}

locals {
    aws_security_group_fam_data_sg_id = "${aws_security_group.fam_data_sg.id}"
}

resource "random_password" "famdb_master_password" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

variable "famdb_master_username" {
  description = "The username for the DB master user"
  type        = string
  default     = "sysadmin"
  sensitive   = true
}

variable "famdb_database_name" {
  description = "The name of the database"
  type        = string
  default     = "famdb"
}

resource "aws_db_subnet_group" "famdb_subnet_group" {
  description = "For Aurora cluster ${var.famdb_cluster_name}"
  name        = "${var.famdb_cluster_name}-subnet-group"
  subnet_ids  = [data.aws_subnet.a_data.id, data.aws_subnet.b_data.id]

  tags = {
    managed-by = "terraform"
  }

  tags_all = {
    managed-by = "terraform"
  }
}

data "aws_rds_engine_version" "postgresql" {
  engine  = "aurora-postgresql"
  version = "16.6"
}

module "aurora_postgresql_v2" {
  source = "terraform-aws-modules/rds-aurora/aws"
  version = "7.7.1"

  name              = var.famdb_cluster_name
  engine            = data.aws_rds_engine_version.postgresql.engine
  engine_mode       = "provisioned"
  engine_version    = data.aws_rds_engine_version.postgresql.version
  storage_encrypted = true
  database_name     = var.famdb_database_name

  vpc_id                 = data.aws_vpc.selected.id
  vpc_security_group_ids = [local.aws_security_group_fam_data_sg_id]
  db_subnet_group_name   = aws_db_subnet_group.famdb_subnet_group.name

  master_username = var.famdb_master_username
  master_password = random_password.famdb_master_password.result

  create_cluster         = true
  create_security_group  = false
  create_db_subnet_group = false
  create_monitoring_role = false
  create_random_password = false

  apply_immediately   = true
  skip_final_snapshot = true
  auto_minor_version_upgrade = false
  allow_major_version_upgrade = true

  db_parameter_group_name         = aws_db_parameter_group.famdb_postgresql.id
  db_cluster_parameter_group_name = aws_rds_cluster_parameter_group.famdb_postgresql.id

  serverlessv2_scaling_configuration = {
    min_capacity = 0.5
    max_capacity = 1
  }

  instance_class = "db.serverless"
  instances = {
    one = {}
    two = {}
  }

  tags = {
    managed-by = "terraform"
  }

  enabled_cloudwatch_logs_exports = ["postgresql"]
}

resource "aws_db_parameter_group" "famdb_postgresql" {
  name_prefix = "${var.famdb_cluster_name}-parameter-group"
  family      = "aurora-postgresql16"
  description = "${var.famdb_cluster_name}-parameter-group"
  tags = {
    managed-by = "terraform"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_rds_cluster_parameter_group" "famdb_postgresql" {
  name_prefix = "${var.famdb_cluster_name}-cluster-parameter-group"
  family      = "aurora-postgresql16"
  description = "${var.famdb_cluster_name}-cluster-parameter-group"
  tags = {
    managed-by = "terraform"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "random_pet" "master_creds_secret_name" {
  prefix = "famdb-master-creds"
  length = 2
}

resource "aws_secretsmanager_secret" "famdb_mastercreds_secret" {
  name = random_pet.master_creds_secret_name.id

  tags = {
    managed-by = "terraform"
  }
}

resource "aws_secretsmanager_secret_version" "famdb_mastercreds_secret_version" {
  secret_id     = aws_secretsmanager_secret.famdb_mastercreds_secret.id
  secret_string = <<EOF
   {
    "username": "${var.famdb_master_username}",
    "password": "${random_password.famdb_master_password.result}"
   }
EOF
}

# Create API Lambda DB User Credentials

resource "random_password" "famdb_api_password" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

variable "famdb_api_username" {
  description = "The username for the DB api user"
  type        = string
  default     = "fam_proxy_api"
  sensitive   = true
}

resource "random_pet" "api_creds_secret_name" {
  prefix = "famdb-api-creds"
  length = 2
}

resource "aws_secretsmanager_secret" "famdb_apicreds_secret" {
  name = random_pet.api_creds_secret_name.id

  tags = {
    managed-by = "terraform"
  }
}

resource "aws_secretsmanager_secret_version" "famdb_apicreds_secret_version" {
  secret_id     = aws_secretsmanager_secret.famdb_apicreds_secret.id
  secret_string = <<EOF
   {
    "username": "${var.famdb_api_username}",
    "password": "${random_password.famdb_api_password.result}"
   }
EOF
}

# Create Admin Management API Lambda DB User Credentials

resource "random_password" "famdb_admin_management_api_password" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

variable "famdb_admin_management_api_username" {
  description = "The username for the DB admin management api user"
  type        = string
  default     = "fam_proxy_admin_management_api"
  sensitive   = true
}

resource "random_pet" "admin_management_api_creds_secret_name" {
  prefix = "famdb-admin-management-api-creds"
  length = 2
}

resource "aws_secretsmanager_secret" "famdb_admin_management_apicreds_secret" {
  name = random_pet.admin_management_api_creds_secret_name.id

  tags = {
    managed-by = "terraform"
  }
}

resource "aws_secretsmanager_secret_version" "famdb_admin_management_apicreds_secret_version" {
  secret_id     = aws_secretsmanager_secret.famdb_admin_management_apicreds_secret.id
  secret_string = <<EOF
   {
    "username": "${var.famdb_admin_management_api_username}",
    "password": "${random_password.famdb_admin_management_api_password.result}"
   }
EOF
}

# Create Auth Lambda DB User Credentials

variable "famdb_auth_lambda_user" {
  description = "The username for the DB auth lambda user"
  type        = string
  default     = "fam_auth_lambda"
  sensitive   = true
}

resource "random_password" "famdb_auth_lambda_password" {
  length           = 20
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "aws_secretsmanager_secret" "famdb_auth_lambda_creds_secret" {
  name = "famdb_auth_lambda_creds_secret"

  tags = {
    managed-by = "terraform"
  }
}

resource "aws_secretsmanager_secret_version" "famdb_auth_lambda_creds_secret_version" {
  secret_id     = aws_secretsmanager_secret.famdb_auth_lambda_creds_secret.id
  secret_string = <<EOF
   {
    "username": "${var.famdb_auth_lambda_user}",
    "password": "${random_password.famdb_auth_lambda_password.result}"
   }
EOF
}


# Creating an rds_proxy object that can be used by the API as a database proxy
# Using the master user secret for now since the api db user does not exist until flyway runs

data "aws_iam_policy_document" "famdb_api_user_rds_proxy_secret_access_policydoc" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["rds.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "famdb_api_user_rds_proxy_secret_access_role" {
  name               = "${var.famdb_cluster_name}-api-proxy-role"
  assume_role_policy = data.aws_iam_policy_document.famdb_api_user_rds_proxy_secret_access_policydoc.json
}

resource "aws_iam_role_policy" "famdb_api_user_rds_proxy_secret_access_policy" {
  name   = "${var.famdb_cluster_name}-api-proxy-role-policy"
  role   = aws_iam_role.famdb_api_user_rds_proxy_secret_access_role.id
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
          "${aws_secretsmanager_secret.famdb_apicreds_secret.arn}",
          "${aws_secretsmanager_secret.famdb_admin_management_apicreds_secret.arn}",
          "${aws_secretsmanager_secret.famdb_auth_lambda_creds_secret.arn}"
        ]
      }
    ]
  }
  EOF
}

resource "aws_db_proxy" "famdb_proxy_api" {
  name                = "${var.famdb_cluster_name}-fam-api-proxy-api"
  debug_logging       = true
  engine_family       = "POSTGRESQL"
  idle_client_timeout = 1800
  require_tls         = false
  role_arn            = aws_iam_role.famdb_api_user_rds_proxy_secret_access_role.arn
  # vpc_security_group_ids = [data.aws_security_group.sg_app.id]
  # vpc_subnet_ids         = [data.aws_subnet.a_datapp_a.id, data.aws_subnet.a_datapp_b.id]
  vpc_security_group_ids = [local.aws_security_group_fam_data_sg_id]
  vpc_subnet_ids         = [data.aws_subnet.a_data.id, data.aws_subnet.b_data.id]


  auth {
    auth_scheme = "SECRETS"
    description = "API Lambda User"
    iam_auth    = "DISABLED"
    secret_arn  = aws_secretsmanager_secret.famdb_apicreds_secret.arn
  }

  auth {
    auth_scheme = "SECRETS"
    description = "Admin Management API Lambda User"
    iam_auth    = "DISABLED"
    secret_arn  = aws_secretsmanager_secret.famdb_admin_management_apicreds_secret.arn
  }

  auth {
    auth_scheme = "SECRETS"
    description = "Auth Lambda User"
    iam_auth    = "DISABLED"
    secret_arn  = aws_secretsmanager_secret.famdb_auth_lambda_creds_secret.arn
  }

  tags = {
    managed-by = "terraform"
  }
}

resource "aws_db_proxy_default_target_group" "famdb_proxy_api_target_group" {
  db_proxy_name = aws_db_proxy.famdb_proxy_api.name

  connection_pool_config {
    connection_borrow_timeout = 120
    # init_query                   = "SET x=1, y=2"
    max_connections_percent      = 100
    max_idle_connections_percent = 50
    # session_pinning_filters      = [ "EXCLUDE_VARIABLE_SETS" ]
  }
}

resource "aws_db_proxy_target" "famdb_proxy_api_target" {
  db_cluster_identifier = module.aurora_postgresql_v2.cluster_id
  db_proxy_name         = aws_db_proxy.famdb_proxy_api.name
  target_group_name     = aws_db_proxy_default_target_group.famdb_proxy_api_target_group.name

  depends_on = [
    module.aurora_postgresql_v2
  ]
}
