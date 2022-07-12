variable "db_instance_name" {
  description = "The name of the database cluster instance"
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
  default     = "fam_api_db_creds"
  sensitive   = true
}