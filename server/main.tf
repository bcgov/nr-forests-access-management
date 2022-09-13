terraform {
  backend "remote" {}
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.14.0"
    }
  }
}


provider "aws" {
  region = var.aws_region
  assume_role {
    role_arn = "arn:aws:iam::${var.target_aws_account_id}:role/BCGOV_${var.target_env}_Automation_Admin_Role"
  }
}

data "aws_vpc" "selected" {
  state = "available"
}

data "aws_subnet" "a" {
  filter {
    name   = "tag:Name"
    values = [var.subnet_a]
  }
}

data "aws_subnet" "b" {
  filter {
    name   = "tag:Name"
    values = [var.subnet_b]
  }
}

data "aws_security_group" "a" {
  filter {
    name   = "tag:Name"
    values = [var.aws_security_group_a]
  }
}

data "aws_subnet" "app_a" {
  filter {
    name   = "tag:Name"
    values = [var.subnet_app_a]
  }
}

data "aws_subnet" "app_b" {
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
