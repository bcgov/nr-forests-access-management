locals {
  flyway_scripts_bucket_name = "fam-cloudfront-bucket-${var.target_env}"
  # fam_waf_cloudfront_resource_name = "fam-${var.target_env}-waf-cloudfront"
}

resource "aws_s3_bucket" "web_distribution" {
  bucket = local.flyway_scripts_bucket_name
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

# data "aws_wafv2_web_acl" "fam_waf_cloudfront" {
#   name   = "${local.fam_waf_cloudfront_resource_name}"
#   scope  = "CLOUDFRONT"
# }

# # TODO: remove this if not working.
# # Try to find a way to reference from "frontend" terraform module to "server" terraform module (but different folders and different apply)
# module "server_info" {
#   source = "../../server"

#   fam_waf_acl_cloudfront_arn = module.fam_waf_acl_cloudfront_arn
# }


# CloudFront WAF ACL  # working!
# resource "aws_wafv2_web_acl" "fam_waf_cloudfront" {
#     name        = "${local.fam_waf_cloudfront_resource_name}"
#     description = "CloudFront WAF Rules"
#     scope       = "CLOUDFRONT"
#     provider    = aws.east # Cloudfront ACL has to be created in this region.

#     default_action {
#         allow {}
#     }


#     ## AWS Managed rules below.
#     rule {
#         name     = "AWS-AWSManagedRulesAmazonIpReputationList"
#         priority = 0

#         override_action {
#             none {}
#         }
#         statement {
#             managed_rule_group_statement {
#                 vendor_name = "AWS"
#                 name        = "AWSManagedRulesAmazonIpReputationList"
#             }
#         }
#         visibility_config {
#             cloudwatch_metrics_enabled = true
#             metric_name                = "${local.fam_waf_cloudfront_resource_name}-AWSManagedRulesAmazonIpReputationList"
#             sampled_requests_enabled   = true
#         }
#     }

#     rule {
#         name     = "AWS-AWSManagedRulesCommonRuleSet"
#         priority = 1

#         override_action {
#             none {}
#         }
#         statement {
#             managed_rule_group_statement {
#                 vendor_name = "AWS"
#                 name        = "AWSManagedRulesCommonRuleSet"
#             }
#         }
#         visibility_config {
#             cloudwatch_metrics_enabled = true
#             metric_name                = "${local.fam_waf_cloudfront_resource_name}-AWSManagedRulesCommonRuleSet"
#             sampled_requests_enabled   = true
#         }
#     }

#     rule {
#         name     = "AWS-AWSManagedRulesKnownBadInputsRuleSet"
#         priority = 2

#         override_action {
#             none {}
#         }
#         statement {
#             managed_rule_group_statement {
#                 vendor_name = "AWS"
#                 name        = "AWSManagedRulesKnownBadInputsRuleSet"
#             }
#         }
#         visibility_config {
#             cloudwatch_metrics_enabled = true
#             metric_name                = "${local.fam_waf_cloudfront_resource_name}-AWSManagedRulesKnownBadInputsRuleSet"
#             sampled_requests_enabled   = true
#         }
#     }

#     rule {
#         name     = "AWS-AWSManagedRulesLinuxRuleSet"
#         priority = 3

#         override_action {
#             none {}
#         }
#         statement {
#             managed_rule_group_statement {
#                 vendor_name = "AWS"
#                 name        = "AWSManagedRulesLinuxRuleSet"
#             }
#         }
#         visibility_config {
#             cloudwatch_metrics_enabled = true
#             metric_name                = "${local.fam_waf_cloudfront_resource_name}-AWSManagedRulesLinuxRuleSet"
#             sampled_requests_enabled   = true
#         }
#     }

#     rule {
#         name     = "AWS-AWSManagedRulesSQLiRuleSet"
#         priority = 4

#         override_action {
#             none {}
#         }
#         statement {
#             managed_rule_group_statement {
#                 vendor_name = "AWS"
#                 name        = "AWSManagedRulesSQLiRuleSet"
#             }
#         }
#         visibility_config {
#             cloudwatch_metrics_enabled = true
#             metric_name                = "${local.fam_waf_cloudfront_resource_name}-AWSManagedRulesSQLiRuleSet"
#             sampled_requests_enabled   = true
#         }
#     }

#     tags = {
#         env = "${var.target_env}"
#         managed-by = "terraform"
#     }

#     visibility_config {
#         cloudwatch_metrics_enabled = true
#         metric_name                = "${local.fam_waf_cloudfront_resource_name}"
#         sampled_requests_enabled   = true
#     }
# }

resource "aws_cloudfront_distribution" "web_distribution" {
  aliases             = ["${var.cloudfront_vanity_domain}"]
  enabled             = true
  is_ipv6_enabled     = true
  wait_for_deployment = false
  default_root_object = "index.html"
  price_class         = "PriceClass_100"
  # web_acl_id          = "${module.server_info.fam_waf_acl_cloudfront_arn}"
  # web_acl_id          = "${data.aws_wafv2_web_acl.fam_waf_cloudfront.arn}"
  web_acl_id          = "${aws_wafv2_web_acl.fam_waf_cloudfront.arn}"

  viewer_certificate {
    # acm_certificate_arn = "${var.cloudfront_certificate_arn}"
    cloudfront_default_certificate = true
    ssl_support_method = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
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
