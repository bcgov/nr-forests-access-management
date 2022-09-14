resource "random_pet" "famdb_cluster_name" {
  prefix = "famdb-cluster"
  length = 2
}

resource "random_pet" "famdb_subnet_group_name" {
  prefix = "famdb-subnet-group"
  length = 2
}

data "aws_kms_alias" "rds_key" {
  name = "alias/aws/rds"
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
  description = "For Aurora cluster ${random_pet.famdb_cluster_name.id}"
  name        = "${random_pet.famdb_cluster_name.id}-subnet-group"
  subnet_ids  = [data.aws_subnet.a.id, data.aws_subnet.b.id]

  tags = {
    managed-by = "terraform"
  }

  tags_all = {
    managed-by = "terraform"
  }
}

# Using example from https://github.com/terraform-aws-modules/terraform-aws-rds-aurora/blob/master/examples/serverless/main.tf

data "aws_rds_engine_version" "postgresql" {
  engine  = "aurora-postgresql"
  version = "13.6"
}

module "aurora_postgresql_v2" {
  source = "terraform-aws-modules/rds-aurora/aws"

  name              = random_pet.famdb_cluster_name.id
  engine            = data.aws_rds_engine_version.postgresql.engine
  engine_mode       = "provisioned"
  engine_version    = data.aws_rds_engine_version.postgresql.version
  storage_encrypted = true
  database_name     = var.famdb_database_name

  vpc_id                 = data.aws_vpc.selected.id
  vpc_security_group_ids = [data.aws_security_group.a.id]
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

  db_parameter_group_name         = aws_db_parameter_group.famdb_postgresql13.id
  db_cluster_parameter_group_name = aws_rds_cluster_parameter_group.famdb_postgresql13.id

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

  enabled_cloudwatch_logs_exports = [ "audit", "error", "general", "slowquery", "postgresql" ]
}

resource "aws_db_parameter_group" "famdb_postgresql13" {
  name        = "${random_pet.famdb_cluster_name.id}-parameter-group"
  family      = "aurora-postgresql13"
  description = "${random_pet.famdb_cluster_name.id}-parameter-group"
  tags = {
    managed-by = "terraform"
  }
}

resource "aws_rds_cluster_parameter_group" "famdb_postgresql13" {
  name        = "${random_pet.famdb_cluster_name.id}-cluster-parameter-group"
  family      = "aurora-postgresql13"
  description = "${random_pet.famdb_cluster_name.id}-cluster-parameter-group"
  tags = {
    managed-by = "terraform"
  }
}

resource "aws_secretsmanager_secret" "famdb_mastercreds_secret" {
  name = "${random_pet.famdb_cluster_name.id}_master_creds"

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

resource "aws_secretsmanager_secret" "famdb_apicreds_secret" {
  name = "${random_pet.famdb_cluster_name.id}_api_creds"

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
  name               = "${random_pet.famdb_cluster_name.id}-api-proxy-role"
  assume_role_policy = data.aws_iam_policy_document.famdb_api_user_rds_proxy_secret_access_policydoc.json
}

resource "aws_iam_role_policy" "famdb_api_user_rds_proxy_secret_access_policy" {
  name   = "${random_pet.famdb_cluster_name.id}-api-proxy-role-policy"
  role   = aws_iam_role.famdb_api_user_rds_proxy_secret_access_role.id
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
          "${aws_secretsmanager_secret.famdb_apicreds_secret.arn}"
        ]
      },
      {
        "Effect": "Allow",
        "Action": "kms:Decrypt",
        "Resource": "arn:aws:kms:region:account_id:key/key_id",
        "Condition": {
          "StringEquals": {
              "kms:ViaService": "secretsmanager.region.amazonaws.com"
          }
        }
      }
    ]
  }
  EOF
}

resource "aws_db_proxy" "famdb_proxy_api" {
  name                = "${random_pet.famdb_cluster_name.id}-fam-api-proxy-api"
  debug_logging       = true
  engine_family       = "POSTGRESQL"
  idle_client_timeout = 1800
  require_tls         = false
  role_arn            = aws_iam_role.famdb_api_user_rds_proxy_secret_access_role.arn
  # vpc_security_group_ids = [data.aws_security_group.sg_app.id]
  # vpc_subnet_ids         = [data.aws_subnet.app_a.id, data.aws_subnet.app_b.id]
  vpc_security_group_ids = [data.aws_security_group.a.id]
  vpc_subnet_ids         = [data.aws_subnet.a.id, data.aws_subnet.b.id]


  auth {
    auth_scheme = "SECRETS"
    description = "example"
    iam_auth    = "DISABLED"
    secret_arn  = aws_secretsmanager_secret.famdb_apicreds_secret.arn
  }

  tags = {
    managed-by = "terraform"
  }
}

resource "aws_db_proxy_default_target_group" "famdb_proxy_api_target_group" {
  db_proxy_name = aws_db_proxy.famdb_proxy_api.name

  connection_pool_config {
    connection_borrow_timeout    = 120
    init_query                   = "SET x=1, y=2"
    max_connections_percent      = 100
    max_idle_connections_percent = 50
    session_pinning_filters      = [ "EXCLUDE_VARIABLE_SETS" ]
  }
}

resource "aws_db_proxy_target" "famdb_proxy_api_target" {
  db_cluster_identifier = module.aurora_postgresql_v2.cluster_id
  db_proxy_name         = aws_db_proxy.famdb_proxy_api.name
  target_group_name     = aws_db_proxy_default_target_group.famdb_proxy_api_target_group.name
}
