resource "aws_security_group" "fam_app_sg" {
    name = "fam_app_sg"
    description = "FAM custom security group for application tier (lambdas)."
    vpc_id = data.aws_vpc.selected.id
    revoke_rules_on_delete = true

    tags = {
        Name = "fam_app_sg"
        managed-by = "terraform"
    }

    ingress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["10.10.32.0/20", "10.10.128.0/20"]
        description = "Central VPC Traffic Inbound from Web subnets"
    }

    ingress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["10.10.0.0/19", "10.10.96.0/19"]
        description = "Central VPC Traffic Inbound from App subnets"
    }

    ingress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["10.10.64.0/21", "10.10.72.0/21"]
        description = "Central VPC Traffic Inbound from Mgmt subnets"
    }

    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
        description = "Allow All Outbound Traffic"
    }

}

resource "aws_security_group" "fam_data_sg" {
    name = "fam_data_sg"
    description = "FAM custom security group for data tier."
    vpc_id = data.aws_vpc.selected.id
    revoke_rules_on_delete = true
    tags = {
        Name = "fam_data_sg"
        managed-by = "terraform"
    }
}

resource "aws_vpc_security_group_ingress_rule" "fam_data_sg_east_west" {
  security_group_id = aws_security_group.fam_data_sg.id
  referenced_security_group_id = aws_security_group.fam_data_sg.id
  ip_protocol = "-1"
  description = "East/West Communication within FAM Data Security Group."
}

resource "aws_vpc_security_group_ingress_rule" "fam_data_sg_postgres" {
  security_group_id = aws_security_group.fam_data_sg.id
  referenced_security_group_id = aws_security_group.fam_app_sg.id
  from_port = 5432
  to_port = 5432
  ip_protocol = "TCP"
  description = "Allow traffic to database from FAM application tier (lambdas)."
}

resource "aws_vpc_security_group_ingress_rule" "fam_data_sg_central_web_a" {
  security_group_id = aws_security_group.fam_data_sg.id
  cidr_ipv4   = "10.10.32.0/20"
  ip_protocol = "-1"
  description = "Central VPC Traffic Inbound from Web-a"
}

resource "aws_vpc_security_group_ingress_rule" "fam_data_sg_central_web_b" {
  security_group_id = aws_security_group.fam_data_sg.id
  cidr_ipv4   = "10.10.128.0/20"
  ip_protocol = "-1"
  description = "Central VPC Traffic Inbound from Web-b"
}

resource "aws_vpc_security_group_ingress_rule" "fam_data_sg_central_app_a" {
  security_group_id = aws_security_group.fam_data_sg.id
  cidr_ipv4   = "10.10.0.0/19"
  ip_protocol = "-1"
  description = "Central VPC Traffic Inbound from App-a"
}

resource "aws_vpc_security_group_ingress_rule" "fam_data_sg_central_app_b" {
  security_group_id = aws_security_group.fam_data_sg.id
  cidr_ipv4   = "10.10.96.0/19"
  ip_protocol = "-1"
  description = "Central VPC Traffic Inbound from App-b"
}

resource "aws_vpc_security_group_ingress_rule" "fam_data_sg_central_mgmt_a" {
  security_group_id = aws_security_group.fam_data_sg.id
  cidr_ipv4   = "10.10.64.0/21"
  ip_protocol = "-1"
  description = "Central VPC Traffic Inbound from Mgmt-a"
}

resource "aws_vpc_security_group_ingress_rule" "fam_data_sg_central_mgmt_b" {
  security_group_id = aws_security_group.fam_data_sg.id
  cidr_ipv4   = "10.10.72.0/21"
  ip_protocol = "-1"
  description = "Central VPC Traffic Inbound from Mgmt-b"
}

resource "aws_vpc_security_group_egress_rule" "fam_data_sg_outbound" {
  security_group_id = aws_security_group.fam_data_sg.id
  cidr_ipv4   = "0.0.0.0/0"
  ip_protocol = "-1"
  description = "Allow All Outbound Traffic"
}
