locals {
    fam_util_ec2_instance_profile_name_prefix = "fam_util_ec2_instance"
}

variable "fam_util_ec2_instance_ami" {
  description = "Instance image for FAM Util EC2"
  type        = string
  # Amazon Linux 2 Kernel 5.10 AMI 2.0.20230119.1 x86_64 HVM gp2
  default     = "ami-047d9348c6bdd7573"
}

variable "fam_util_ec2_instance_type" {
  description = "Instance type to use for the instance"
  type        = string
  default     = "t3.small"
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
  # Exit immediately on error, undefined variable, or pipeline error
  set -euo pipefail

  # Log all output to a file
  exec > /var/log/user-data.log 2>&1

  echo "[INFO] Starting EC2 initialization..."

  # Update packages
  echo "[INFO] Updating system packages..."
  sudo dnf update -y

  # Install PostgreSQL 16 repo (Fedora 38 version for Amazon Linux 2023)
  echo "[INFO] Adding PostgreSQL 16 repository..."
  sudo dnf install -y https://download.postgresql.org/pub/repos/yum/16/fedora/fedora-38-x86_64/pgdg-redhat-repo-latest.noarch.rpm

  # Disable default PostgreSQL module to avoid conflicts
  echo "[INFO] Disabling default PostgreSQL module..."
  sudo dnf -qy module disable postgresql

  # Install only PostgreSQL 16 client (psql)
  echo "[INFO] Installing psql 16..."
  sudo dnf install -y postgresql16

  # Verify psql installation
  echo "[INFO] Verifying installation..."
  psql --version

  echo "[SUCCESS] psql 16 installation completed."


  # #!/bin/bash
  # echo "Installing postgresql.x86_64" > init.log
  # sudo yum update -y >> init.log 2>&1 &
  # sudo yum install -y postgresql.x86_64 >> init.log 2>&1 &
  # echo "Postgres installation done" >> init.log

  EOF

}

resource "aws_ec2_instance_state" "fam_util_ec2_instance_state" {
  instance_id = aws_instance.fam_util_ec2_instance.id
  # fam_util_ec2_instance instance created in dormant state.
  state       = "stopped"
}

resource "aws_iam_instance_profile" "fam_util_ec2_instance_profile" {
  name = "${local.fam_util_ec2_instance_profile_name_prefix}_instance_profile"
  role = "EC2-Default-SSM-AD-Role" # default role given by ASEA platform, can't change.
}