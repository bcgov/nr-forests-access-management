variable "target_env" {
  description = "AWS workload account env (e.g. dev, test, prod, sandbox, unclass)"
}

variable "target_aws_account_id" {
  description = "AWS workload account id"
}

variable "aws_region" {
  description = "AWS region for all resources."

  type    = string
  default = "ca-central-1"
}

variable "db_cluster_identifier" {
  description = "The idsentifier of the database cluster"
  type        = string
  default     = "fam-aurora-db-postgres"
}

variable "db_name" {
  description = "The name of the database"
  type        = string
  default     = "famdb"
}

variable "db_api_creds_secretname" {
  description = "The name of the AWS Secret that holds the FAM api db username/password"
  type        = string
  default     = "fam_api_db_creds2"
  sensitive   = true
}

variable "github_repository" {
  type = string
}

variable "git_branch" {
  type = string
}
