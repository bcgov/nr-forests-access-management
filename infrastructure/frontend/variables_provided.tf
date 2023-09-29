variable "target_env" {
  description = "AWS workload account env"
  type        = string
}

variable "cloudfront_vanity_domain" {
  description = "Alternate vanity domain to use for cloudfront distribution for frontend"
  type = string
}

variable "cloudfront_certificate_arn" {
  description = "ARN for certificate to use in cloudfront"
  type = string
}