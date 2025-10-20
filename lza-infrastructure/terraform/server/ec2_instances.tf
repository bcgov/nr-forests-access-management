locals {
    fam_util_ec2_instance_profile_name_prefix = "fam_util_ec2_instance"
}

variable "fam_util_ec2_instance_ami" {
  description = "Instance image for FAM Util EC2"
  type        = string
  # Amazon Linux 2023 (kernel-6.1)
  default     = "ami-06131bddb5c4ff9ac"
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

  user_data = <<-EOF
#!/bin/bash
set -e

LOGFILE="/var/log/init-postgresql-install.log"

# Redirect all output (stdout & stderr) to both logfile and console
exec > >(tee -a "$LOGFILE") 2>&1

echo "[INFO] Starting initialization..."

# Wait for DNS resolution (amazonlinux.com chosen as stable)
MAX_RETRIES=30
COUNT=0
until host amazonlinux.com >/dev/null 2>&1; do
    let COUNT=COUNT+1
    if [ "$COUNT" -ge "$MAX_RETRIES" ]; then
        echo "[ERROR] DNS not available after retry. Check VPC/NAT/S3 endpoint."
        exit 1
    fi
    echo "[INFO] Waiting for DNS to be ready..."
    sleep 2
done

# Wait for dnf repo to be available
for i in {1..10}; do
    if dnf repolist &>/dev/null; then
        echo "[INFO] Network and package repo ready."
        break
    else
        echo "[INFO] Waiting for package repo..."
        sleep 5
    fi
done

# Install only PostgreSQL 16 client
echo "[INFO] Installing psql 16..."
dnf install -y postgresql16

# Verify psql installation
echo "[INFO] Verifying installation..."
psql --version

echo "[SUCCESS] psql 16 installation completed."
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