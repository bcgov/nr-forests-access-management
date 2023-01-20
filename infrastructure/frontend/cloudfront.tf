
resource "random_pet" "lambda_bucket_name" {
  prefix = "ssp-testing-bucket"
  length = 4
}

resource "aws_s3_bucket" "web_distribution" {
  bucket = random_pet.lambda_bucket_name.id
  #acl    = "public-read"

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
  aliases             = ["fam-dev.nrs.gov.bc.ca"]
  enabled             = true
  is_ipv6_enabled     = true
  wait_for_deployment = false
  default_root_object = "index.html"
  price_class         = "PriceClass_100"

  viewer_certificate {
    acm_certificate_arn = "arn:aws:acm:us-east-1:521834415778:certificate/d9407a0e-98b4-47d0-be73-adefe7011d34"
  }

  origin {
    domain_name = aws_s3_bucket.web_distribution.bucket_regional_domain_name
    origin_id   = "web_distribution_origin"
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.web_distribution.cloudfront_access_identity_path
    }
  }

  # Required for SPA application to redirect requests to deep links to root, which loads index.html, which loads the Vue app
  # and then the Vue router properly resolves the deep link.
  custom_error_response {
    error_code = 403
    response_code = 200
    response_page_path = "/"
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

  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations        = ["CA", "US"]
    }
  }
}

locals {
  src_dir = "./dist/"
  content_type_map = {
    html = "text/html",
    ico  = "image/x-icon",
    js   = "application/javascript",
    json = "application/json",
    svg  = "image/svg+xml",
    ttf  = "font/ttf",
    txt  = "text/txt",
    css  = "text/css"
  }
  files_raw = fileset(local.src_dir, "**")
  files = toset([
    for jsFile in local.files_raw:
      jsFile if jsFile != ".terragrunt-source-manifest" && jsFile != "assets/.terragrunt-source-manifest"
  ])
}

resource "aws_s3_bucket_object" "site_files" {
  # for_each = fileset(local.src_dir, "**")
  for_each = local.files

  # Create an object from each
  bucket = aws_s3_bucket.web_distribution.id
  key    = each.value
  source = "${local.src_dir}/${each.value}"
  etag = filemd5("${local.src_dir}/${each.value}")

  content_type = lookup(local.content_type_map, regex("\\.(?P<extension>[A-Za-z0-9]+)$", each.value).extension, "application/octet-stream")
}
