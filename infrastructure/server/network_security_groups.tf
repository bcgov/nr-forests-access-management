resource "aws_security_group" "fam_app_sg" {
    name = "fam_app_sg"
    description = "FAM custom security group for application tier (lambdas)."
    vpc_id = data.aws_vpc.selected.id
    revoke_rules_on_delete = true

    tags = {
        Name = "fam_app_sg"
        managed-by = "terraform"
    }

}

resource "aws_vpc_security_group_egress_rule" "fam_app_sg_outbound" {
  security_group_id = aws_security_group.fam_app_sg.id
  cidr_ipv4   = "0.0.0.0/0"
  ip_protocol = "-1"
  description = "Allow All Outbound Traffic"
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

resource "aws_vpc_security_group_egress_rule" "fam_data_sg_outbound" {
  security_group_id = aws_security_group.fam_data_sg.id
  cidr_ipv4   = "0.0.0.0/0"
  ip_protocol = "-1"
  description = "Allow All Outbound Traffic"
}
