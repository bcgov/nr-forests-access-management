variable "aws_security_group_data" {
  description = "Value of the name tag for the DATA security group"
  default     = "Data_sg"
}

variable "subnet_data_a" {
  description = "Value of the name tag for a subnet in the DATA security group"
  default     = "Data_Dev_aza_net"
}

variable "subnet_data_b" {
  description = "Value of the name tag for a subnet in the DATA security group"
  default     = "Data_Dev_azb_net"
}


variable "aws_security_group_app" {
  description = "Value of the name tag for the APP security group"
  default     = "App_sg"
}

variable "subnet_app_a" {
  description = "Value of the name tag for a subnet in the APP security group"
  default     = "App_Dev_aza_net"
}

variable "subnet_app_b" {
  description = "Value of the name tag for a subnet in the APP security group"
  default     = "App_Dev_azb_net"
}