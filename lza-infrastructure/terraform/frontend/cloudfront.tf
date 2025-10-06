locals {
  flyway_scripts_bucket_name = "fam-cloudfront-bucket-${var.licence_plate}-${var.target_env}"
  web_distribution_origin_id = "web_distribution_origin"
  consumer_fam_api_origin_id = "consumer_fam_api_gateway_origin"
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

data "aws_region" "current" {}

data "aws_api_gateway_rest_api" "fam_api_gateway_rest_api" {
  name = "fam-api-lambda-tools-gateway"   # must match name in api-gateway.tf
}

/*
This is the CloudFront distribution for the FAM web application and the FAM Consumer API (API Gateway).
It has two origins:
1. S3 bucket origin for the web application static files
2. API Gateway origin for the FAM Consumer API

Note! Initially the distribution was named "web_distribution" because it only had S3 origin for the web app.
      Do not rename it to other distribution resource name as Terraform will destroy and recreate the distribution
      resource (with new distribution domain name) and that will cause DNS (custom domain) entry to fail due to the
      target distribution domain name change; and deployment will fail at frontend and distribution will be empty.
*/
resource "aws_cloudfront_distribution" "web_distribution" {
  # aliases             = ["${var.cloudfront_vanity_domain}"]
  enabled             = true
  is_ipv6_enabled     = true
  wait_for_deployment = false
  default_root_object = "index.html"
  price_class         = "PriceClass_100"
  web_acl_id          = "${aws_wafv2_web_acl.fam_waf_cloudfront.arn}"

  viewer_certificate {
    # acm_certificate_arn = "${var.cloudfront_certificate_arn}"
    # ssl_support_method = "sni-only"
    # minimum_protocol_version = "TLSv1.2_2021"

    cloudfront_default_certificate = true  # TODO: remove this after certificate is issued and in place and adjust above. Use AWS default for now.
  }

  # web distribution S3 origin
  origin {
    domain_name = aws_s3_bucket.web_distribution.bucket_regional_domain_name
    origin_id   = local.web_distribution_origin_id
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.web_distribution.cloudfront_access_identity_path
    }
  }

  # FAM API API Gateway origin
  origin {
    domain_name = "${data.aws_api_gateway_rest_api.fam_api_gateway_rest_api.id}.execute-api.${data.aws_region.current.name}.amazonaws.com"
    origin_id   = local.consumer_fam_api_origin_id
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]

      connection_attempts      = 3        # default is 3
      origin_read_timeout      = 60      # default is 30, increase for cold starts
      connection_timeout       = 15       # default is 10
      origin_keepalive_timeout = 15       # default is 5, increase for persistent connections
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
    target_origin_id = local.web_distribution_origin_id

    forwarded_values {
      query_string = true
      cookies {
        forward = "none"
      }
      headers = ["Origin"]
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 300
    max_ttl                = 86400
  }

  # FAM Consumer API API Gateway origin behavior
  /*
  This maps request URL path "/api/..." to API Gateway origin.
  Reference to https://apps.nrs.gov.bc.ca/int/confluence/display/FSAST1/Users+Search+API for external consumer API specs.
  Consumer API uses custom domain with intended path "/api/*" mapping. E.g., /api/external/v1/users
  */
  ordered_cache_behavior {
    # maps request URL path "/api/..." to API Gateway origin
    path_pattern           = "/api/*"
    target_origin_id       = local.consumer_fam_api_origin_id

    viewer_protocol_policy = "https-only"
    allowed_methods        = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods         = ["GET", "HEAD", "OPTIONS"]

    # using AWS managed CachingDisabled policy (Recommended for API Gateway)
    cache_policy_id    = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"

    # using AWS managed AllViewerExceptHostHeader policy (Recommended for API Gateway)
    origin_request_policy_id = "b689b0a8-53d0-40ab-baf2-68738e2966ac"

    # Link function to rewrite /api/... to /v1/... (API Gateway stage name is 'v1')
    function_association {
      event_type   = "viewer-request"
      function_arn = aws_cloudfront_function.fam_api_viewer_request_function.arn
    }
  }

  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations        = ["CA", "US"]
    }
  }

  lifecycle {
    prevent_destroy = true
  }

}

/*
This is the CloudFront function for the FAM API Gateway viewer request.
API Gateway stage name is 'v1', need to rewrite /api/... to /v1/...
It rewrites the request path from /api/... to /v1/... so that the API Gateway can route it properly.
*/
resource "aws_cloudfront_function" "fam_api_viewer_request_function" {
  name    = "fam-${var.licence_plate}-${var.target_env}-api-viewer-request-rewriteApiPath-function" # needs global uniqueness
  runtime = "cloudfront-js-2.0"

  comment = "Viewer request function for API Gateway origin to rewrite /api/... path to /v1/... path"

  code = <<EOF
function handler(event) {
  var request = event.request;
  // Add custom headers
  request.headers["x-env"] = { value: "FAM_${var.target_env}" };
  request.headers["x-request-id"] = { value: `$${Math.random().toString(36).substring(2)}-$${new Date().toISOString()}` };

  // Rewrite /api/* to /v1/*
  if (request.uri.startsWith("/api/")) {
      request.uri = request.uri.replace("/api/", "/v1/");
  }

  return request;
}
EOF
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
    css  = "text/css",
    pdf  = "application/pdf"
  }
  ignore_files = [".terragrunt-source-manifest","assets/.terragrunt-source-manifest","files/.terragrunt-source-manifest"]
  files_raw = fileset(local.src_dir, "**")
  files = toset([
    for jsFile in local.files_raw:
      jsFile if !contains(local.ignore_files, jsFile)
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

  content_type = lookup(local.content_type_map, regex("\\.(?P<extension>[A-Za-z0-9_]+)$", each.value).extension, "application/octet-stream")
}
