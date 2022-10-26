data "aws_vpc" "selected" {
  state = "available"
}


data "aws_security_group" "sg_data" {
  filter {
    name   = "tag:Name"
    values = [var.aws_security_group_data]
  }
}

data "aws_subnet" "a_data" {
  filter {
    name   = "tag:Name"
    values = [var.subnet_data_a]
  }
}

data "aws_subnet" "b_data" {
  filter {
    name   = "tag:Name"
    values = [var.subnet_data_b]
  }
}

data "aws_subnet" "a_app" {
  filter {
    name   = "tag:Name"
    values = [var.subnet_app_a]
  }
}

data "aws_subnet" "b_app" {
  filter {
    name   = "tag:Name"
    values = [var.subnet_app_b]
  }
}

data "aws_security_group" "sg_app" {
  filter {
    name   = "tag:Name"
    values = [var.aws_security_group_app]
  }
}
