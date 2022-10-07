terraform {
 backend "remote" {}
required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "3.9.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  assume_role {
    role_arn = "arn:aws:iam::${var.target_aws_account_id}:role/BCGOV_${var.target_env}_Automation_Admin_Role"
  }
}

resource "random_pet" "lambda_bucket_name" {
  prefix = "ssp-testing-bucket"
  length = 4
}

resource "aws_s3_bucket" "web_distribution" {
  bucket = random_pet.lambda_bucket_name.id
  # acl    = "private"
}
resource "aws_cloudfront_origin_access_identity" "web_distribution" {
}
data "aws_iam_policy_document" "web_distribution" {
  statement {
    actions = ["s3:GetObject"]
    principals {
      type        = "AWS"
      identifiers = ["${aws_cloudfront_origin_access_identity.web_distribution.iam_arn}"]
    }
    resources = ["${aws_s3_bucket.web_distribution.arn}/*"]
  }
}

resource "aws_s3_bucket_policy" "web_distribution" {
  bucket = aws_s3_bucket.web_distribution.id
  policy = data.aws_iam_policy_document.web_distribution.json
}
resource "aws_cloudfront_distribution" "web_distribution" {
  enabled             = true
  is_ipv6_enabled     = true
  wait_for_deployment = false
  default_root_object = "index.html"
  price_class         = "PriceClass_100"

  origin {
    domain_name = aws_s3_bucket.web_distribution.bucket_regional_domain_name
    origin_id   = "web_distribution_origin"
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.web_distribution.cloudfront_access_identity_path
    }
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = "web_distribution_origin"

    forwarded_values {
      query_string = true
      cookies {
        forward = "none"
      }
      headers = ["Origin"]
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400


  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations        = ["CA", "US"]
    }
  }
}
locals {
  src_dir = "./build/"
  content_type_map = {
    html = "text/html",
    ico  = "image/x-icon",
    js   = "application/javascript",
    json = "application/json",
    svg  = "image/svg+xml",
    ttf  = "font/ttf",
    txt  = "text/txt"

  }
}

resource "aws_s3_bucket_object" "site_files" {
  # Enumerate all the files in ./src
  for_each = fileset(local.src_dir, "**")

  # Create an object from each
  bucket = aws_s3_bucket.web_distribution.id
  key    = each.value
  source = "${local.src_dir}/${each.value}"

  content_type = lookup(local.content_type_map, regex("\\.(?P<extension>[A-Za-z0-9]+)$", each.value).extension, "application/octet-stream")
}
