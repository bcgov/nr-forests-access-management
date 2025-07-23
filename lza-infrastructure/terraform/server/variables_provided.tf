variable "target_env" {
  description = "AWS workload account env"
  type        = string
}

# Networking Variables
variable "subnet_data_a" {
  description = "Value of the name tag for a subnet in the DATA security group"
  type = string
}

variable "subnet_data_b" {
  description = "Value of the name tag for a subnet in the DATA security group"
  type = string
}

variable "subnet_app_a" {
  description = "Value of the name tag for a subnet in the APP security group"
  type = string
}

variable "subnet_app_b" {
  description = "Value of the name tag for a subnet in the APP security group"
  type = string
}

variable "subnet_web_a" {
  description = "Value of the name tag for a subnet in the Web security group"
  type = string
}

variable "subnet_web_b" {
  description = "Value of the name tag for a subnet in the Web security group"
  type = string
}