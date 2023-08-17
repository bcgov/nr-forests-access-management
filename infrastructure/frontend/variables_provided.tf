
variable "cloudfront_vanity_domain" {
  description = "Alternate vanity domain to use for cloudfront distribution for frontend"
  type = string
}

variable "cloudfront_certificate_arn" {
  description = "ARN for certificate to use in cloudfront"
  type = string
}

# variable "fam_waf_acl_cloudfront_arn" {
#   description = "The ARN of the WAF ACL Cloudfront"
#   type = string
# }