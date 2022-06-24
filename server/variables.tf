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

variable "aws_security_group_a" {
  description = "Value of the name tag for the security group in AZ a"
  default     = "Data_sg"
}

variable "subnet_a" {
  description = "Value of the name tag for the subnet in AZ a"
  default     = "Data_Dev_aza_net"
}

variable "subnet_b" {
  description = "Value of the name tag for the subnet in AZ b"
  default     = "Data_Dev_azb_net"
}

variable "db_name" {
  description = "The name of the database"
  type        = string
  default     = "famdb"
}

variable "db_username" {
  description = "The username for the DB master user"
  type        = string
  default     = "sysadmin"
  sensitive   = true
}

# variable "db_password" {
#   description = "The password for the DB master user"
#   type        = string
#   default     = environment.
#   sensitive   = true
# }