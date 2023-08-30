resource "aws_security_group" "basil-test" {
    name = "basil-test"
    description = "this is a description"
    vpc_id = data.aws_vpc.selected.id
    revoke_rules_on_delete = true

    tags = {
        managed-by = "terraform"
    }

}