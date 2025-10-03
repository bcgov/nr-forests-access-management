output "cf_domain_name" {
  value       = try(aws_cloudfront_distribution.fam_distribution.domain_name, "")
  description = "Domain name corresponding to the distribution"
}
