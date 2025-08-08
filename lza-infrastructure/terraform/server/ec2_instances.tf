locals {
    fam_util_ec2_instance_profile_name_prefix = "fam_util_ec2_instance"
}

variable "fam_util_ec2_instance_ami" {
  description = "Instance image for FAM Util EC2"
  type        = string
  # Amazon Linux 2 Kernel 5.10 AMI 2.0.20230119.1 x86_64 HVM gp2
  default     = "ami-092e716d46cd65cac"
}

variable "fam_util_ec2_instance_type" {
  description = "Instance type to use for the instance"
  type        = string
  default     = "t2.micro"
}

resource "aws_instance" "fam_util_ec2_instance" {
  ami                     = "${var.fam_util_ec2_instance_ami}"
  instance_type           = "${var.fam_util_ec2_instance_type}"
  subnet_id = data.aws_subnet.a_app.id
  vpc_security_group_ids = ["${aws_security_group.fam_app_sg.id}"]

  depends_on = [aws_security_group.fam_app_sg]

  iam_instance_profile = "${aws_iam_instance_profile.fam_util_ec2_instance_profile.id}"

  root_block_device {
    # At default, this is not set.
    encrypted = true
  }

  metadata_options {
    # Enable IMDSv2 (Instance Metadata Service Version 2)
    http_tokens = "required"
  }

  # Detail AWS monitoring enabled for security.
  monitoring = true

  tags = {
      Name = "fam_util_ec2_host"
      managed-by = "terraform"
  }

  # Script to install postgresql.
  user_data = <<EOF
  #!/bin/bash
  set -e

  LOGFILE="/var/log/init-postgresql-install.log"

  echo "Starting PostgreSQL client installation..." | tee -a $LOGFILE

  # Enable PostgreSQL 14 repo from Amazon Linux Extras
  sudo amazon-linux-extras enable postgresql14 | tee -a $LOGFILE

  # Clean yum metadata cache
  sudo yum clean metadata | tee -a $LOGFILE

  # Install PostgreSQL 14 client (postgresql package will point to 14 now)
  sudo yum install -y postgresql | tee -a $LOGFILE

  echo "PostgreSQL client installation complete." | tee -a $LOGFILE
  EOF
}

resource "aws_ec2_instance_state" "fam_util_ec2_instance_state" {
  instance_id = aws_instance.fam_util_ec2_instance.id
  # fam_util_ec2_instance instance created in dormant state.
  state       = "stopped"
}

resource "aws_iam_instance_profile" "fam_util_ec2_instance_profile" {
  name = "${local.fam_util_ec2_instance_profile_name_prefix}_instance_profile"
  role = "EC2-Default-SSM-AD-Role" # default role given by LZA platform.
}