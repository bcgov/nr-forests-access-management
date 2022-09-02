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
  override_special = "_%@"
}

variable "famdb_master_username" {
  description = "The username for the DB master user"
  type        = string
  default     = "sysadmin"
  sensitive   = true
}

resource "aws_rds_cluster" "famdb_cluster" {
  allocated_storage                   = "1"
  availability_zones                  = ["ca-central-1a", "ca-central-1b"]
  backtrack_window                    = "0"
  backup_retention_period             = "7"
  cluster_identifier                  = random_pet.famdb_cluster_name.id
  cluster_members                     = [aws_db_instance.famdb_cluster_ca_central_1a.id, aws_db_instance.famdb_cluster_ca_central_1b.id]
  copy_tags_to_snapshot               = "true"
  db_cluster_parameter_group_name     = "default.aurora-postgresql13"
  db_subnet_group_name                = aws_db_subnet_group.famdb_subnet_group.name
  deletion_protection                 = "true"
  enable_http_endpoint                = "false"
  engine                              = "aurora-postgresql"
  engine_mode                         = "provisioned"
  engine_version                      = "13.7"
  iam_database_authentication_enabled = "false"
  iops                                = "0"
  kms_key_id                          = data.aws_kms_alias.rds_key.id
  master_username                     = var.famdb_master_username
  master_password                     = random_password.db_password.result
  port                                = "5432"
  preferred_backup_window             = "08:49-09:19"
  preferred_maintenance_window        = "wed:09:21-wed:09:51"

  serverlessv2_scaling_configuration {
    max_capacity = "64"
    min_capacity = "8"
  }

  storage_encrypted      = "true"
  vpc_security_group_ids = [data.aws_security_group.a.id]

  tags = {
    managed-by = "terraform"
  }
}

resource "aws_db_instance" "famdb_cluster_ca_central_1a" {
  allocated_storage                   = "1"
  auto_minor_version_upgrade          = "true"
  availability_zone                   = "ca-central-1a"
  backup_retention_period             = "7"
  backup_window                       = "08:49-09:19"
  ca_cert_identifier                  = "rds-ca-2019"
  copy_tags_to_snapshot               = "false"
  customer_owned_ip_enabled           = "false"
  db_subnet_group_name                = aws_db_subnet_group.famdb_subnet_group.name
  deletion_protection                 = "false"
  engine                              = "aurora-postgresql"
  engine_version                      = "13.7"
  iam_database_authentication_enabled = "false"
  identifier                          = "${random_pet.famdb_cluster_name.id}-ca-central-1a"
  instance_class                      = "db.serverless"
  kms_key_id                          = data.aws_kms_alias.rds_key.id
  license_model                       = "postgresql-license"
  maintenance_window                  = "tue:05:31-tue:06:01"
  max_allocated_storage               = "0"
  # only for enhanced monitoring metrics sent to CloudWatch logs
  #   monitoring_interval                   = "60"
  #   monitoring_role_arn                   = "arn:aws:iam::521834415778:role/rds-monitoring-role"
  multi_az                              = "false"
  option_group_name                     = "default:aurora-postgresql-13"
  parameter_group_name                  = "default.aurora-postgresql13"
  performance_insights_enabled          = "false"
  performance_insights_retention_period = "0"
  port                                  = "5432"
  publicly_accessible                   = "false"
  storage_encrypted                     = "true"
  storage_type                          = "gp2"
  username                              = var.famdb_master_username
  password                              = random_password.db_password.result
  vpc_security_group_ids                = [data.aws_security_group.a.id]

  tags = {
    managed-by = "terraform"
  }

}

resource "aws_db_instance" "famdb_cluster_ca_central_1b" {
  allocated_storage                   = "1"
  auto_minor_version_upgrade          = "true"
  availability_zone                   = "ca-central-1b"
  backup_retention_period             = "7"
  backup_window                       = "08:49-09:19"
  ca_cert_identifier                  = "rds-ca-2019"
  copy_tags_to_snapshot               = "false"
  customer_owned_ip_enabled           = "false"
  db_subnet_group_name                = aws_db_subnet_group.famdb_subnet_group.name
  deletion_protection                 = "false"
  engine                              = "aurora-postgresql"
  engine_version                      = "13.7"
  iam_database_authentication_enabled = "false"
  identifier                          = "${random_pet.famdb_cluster_name.id}-ca-central-1b"
  instance_class                      = "db.serverless"
  kms_key_id                          = data.aws_kms_alias.rds_key.id
  license_model                       = "postgresql-license"
  maintenance_window                  = "thu:06:54-thu:07:24"
  max_allocated_storage               = "0"
  # only for enhanced monitoring metrics sent to CloudWatch logs
  #   monitoring_interval                   = "60"
  #   monitoring_role_arn                   = "arn:aws:iam::521834415778:role/rds-monitoring-role"
  multi_az                              = "false"
  option_group_name                     = "default:aurora-postgresql-13"
  parameter_group_name                  = "default.aurora-postgresql13"
  performance_insights_enabled          = "false"
  performance_insights_retention_period = "0"
  port                                  = "5432"
  publicly_accessible                   = "false"
  storage_encrypted                     = "true"
  storage_type                          = "gp2"
  username                              = var.famdb_master_username
  password                              = random_password.db_password.result
  vpc_security_group_ids                = [data.aws_security_group.a.id]

  tags = {
    managed-by = "terraform"
  }

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

resource "random_pet" "famdb_mastercreds_secret_name" {
  prefix = "famdb-mastercreds-secret"
  length = 8
}

resource "aws_secretsmanager_secret" "famdb_mastercreds_secret" {
   name = random_pet.famdb_mastercreds_secret_name.id
}

resource "aws_secretsmanager_secret_version" "famdb_mastercreds_secret_version" {
  secret_id = aws_secretsmanager_secret.secretmasterDB.id
  secret_string = <<EOF
   {
    "username": "${var.famdb_master_username}",
    "password": "${random_password.db_password.result}"
   }
EOF
}

# resource "random_pet" "famdb_apicreds_secret_name" {
#   prefix = "famdb-apicreds-secret"
#   length = 8
# }

# resource "random_pet" "famdb_apicreds_proxy_name" {
#   prefix = "famdb-apicreds-proxy"
#   length = 8
# }
