resource "aws_kms_key" "bcsc_key" {
  customer_master_key_spec = "RSA_2048"
  description              = "Key designed for BCSC encryption. They read the public and only we can decrypt (using the private)"
  enable_key_rotation      = "false"
  is_enabled               = "true"
  key_usage                = "ENCRYPT_DECRYPT"
  multi_region             = "false"
}

data "aws_caller_identity" "current" {}

resource "aws_kms_key_policy" "bcsc_key_policy" {
  key_id = aws_kms_key.bcsc_key.id
  policy = jsonencode({
    Id = "bcsc_key_policy"
    Statement = [
      {
        Action = "kms:*"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }

        Resource = "*"
        Sid      = "Enable IAM User Permissions"
      },
    ]
    Version = "2012-10-17"
  })
}

