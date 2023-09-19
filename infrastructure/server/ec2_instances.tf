
variable "fam_bastion_host_instance_ami" {
  description = "Instance image for Bastion Host"
  type        = string
  # Amazon Linux 2 Kernel 5.10 AMI 2.0.20230119.1 x86_64 HVM gp2
  default     = "ami-092e716d46cd65cac"
}

variable "fam_bastion_host_instance_type" {
  description = "Instance type to use for the instance"
  type        = string
  default     = "t2.micro"
}

resource "aws_instance" "fam_bastion_host" {
  ami                     = "${var.fam_bastion_host_instance_ami}"
  instance_type           = "${var.fam_bastion_host_instance_type}"
  subnet_id = data.aws_subnet.a_app.id
  vpc_security_group_ids = ["${aws_security_group.fam_app_sg.id}"]

  depends_on = [aws_security_group.fam_app_sg]

  iam_instance_profile = "${aws_iam_instance_profile.fam_ec2_bastion_host_profile.id}"

  tags = {
      Name = "fam_bastion_host"
      managed-by = "terraform"
  }
  user_data = <<EOF
  #!/bin/bash
  echo "Installing postgresql15.x86_64" > init.log
  sudo yum update
  sudo yum install postgresql15.x86_64
  echo "Postgres installation done" >> init.log

  EOF
}

resource "aws_ec2_instance_state" "fam_bastion_host_state" {
  instance_id = aws_instance.fam_bastion_host.id
  # fam_bastion_host instance created in dormant state.
  state       = "stopped"
}

# TODO: experimeting on permission below.
resource "aws_iam_instance_profile" "fam_ec2_bastion_host_profile" {
  name = "${aws_instance.fam_bastion_host}_instance_profile"
  role = "${aws_iam_role.fam_ec2_bastion_host_role.name}"
}

resource "aws_iam_role" "fam_ec2_bastion_host_role" {
  name = "${aws_instance.fam_bastion_host}_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}

  EOF
}