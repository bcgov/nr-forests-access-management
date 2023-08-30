resource "aws_security_group" "test_app_sg" {
    name = "basil-test"
    description = "FAM custom security group for application tier (lambdas)."
    vpc_id = data.aws_vpc.selected.id
    revoke_rules_on_delete = true

    tags = {
        Name = "test_app_sg"
        managed-by = "terraform"
    }

    ingress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["10.10.32.0/20", "10.10.128.0/20"]
        description = "Allow all inbound from Shared Services Web subnets"
    }

    egress {
        from_port = 0
        to_port = 0
        protocol = "-1"
        cidr_blocks = ["0.0.0.0/0"]
        description = "Allow all outbound traffic"
    }

}
