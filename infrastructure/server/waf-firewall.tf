locals {
    # Example: "fam-dev-waf"
    web_acl_name_prefix = "fam-${var.target_env}-waf"
}


# API-Gateway WAF ACL
resource "aws_wafv2_web_acl" "fam_waf_api_gateway" {
    name        = "${web_acl_name_prefix}-apigateway"
    description = "API Gateway WAF Rules"
    scope       = "REGIONAL"

    default_action {
        allow {}
    }


    ## AWS Managed rules below.
    rule {
        name     = "AWS-AWSManagedRulesAmazonIpReputationList"
        priority = 0

        override_action {
            none {}
        }
        statement {
            managed_rule_group_statement {
                vendor_name = "AWS"
                name        = "AWSManagedRulesAmazonIpReputationList"
            }
        }
        visibility_config {
            cloudwatch_metrics_enabled = true
            metric_name                = "${aws_wafv2_web_acl.fam_waf_api_gateway.name}-AWSManagedRulesAmazonIpReputationList"
            sampled_requests_enabled   = true
        }
    }

    rule {
        name     = "AWS-AWSManagedRulesCommonRuleSet"
        priority = 1

        override_action {
            none {}
        }
        statement {
            managed_rule_group_statement {
                vendor_name = "AWS"
                name        = "AWSManagedRulesCommonRuleSet"
            }
        }
        visibility_config {
            cloudwatch_metrics_enabled = true
            metric_name                = "${aws_wafv2_web_acl.fam_waf_api_gateway.name}-AWSManagedRulesCommonRuleSet"
            sampled_requests_enabled   = true
        }
    }

    rule {
        name     = "AWS-AWSManagedRulesKnownBadInputsRuleSet"
        priority = 2

        override_action {
            none {}
        }
        statement {
            managed_rule_group_statement {
                vendor_name = "AWS"
                name        = "AWSManagedRulesKnownBadInputsRuleSet"
            }
        }
        visibility_config {
            cloudwatch_metrics_enabled = true
            metric_name                = "${aws_wafv2_web_acl.fam_waf_api_gateway.name}-AWSManagedRulesKnownBadInputsRuleSet"
            sampled_requests_enabled   = true
        }
    }

    rule {
        name     = "AWS-AWSManagedRulesLinuxRuleSet"
        priority = 3

        override_action {
            none {}
        }
        statement {
            managed_rule_group_statement {
                vendor_name = "AWS"
                name        = "AWSManagedRulesLinuxRuleSet"
            }
        }
        visibility_config {
            cloudwatch_metrics_enabled = true
            metric_name                = "${aws_wafv2_web_acl.fam_waf_api_gateway.name}-AWSManagedRulesLinuxRuleSet"
            sampled_requests_enabled   = true
        }
    }

    rule {
        name     = "AWS-AWSManagedRulesSQLiRuleSet"
        priority = 4

        override_action {
            none {}
        }
        statement {
            managed_rule_group_statement {
                vendor_name = "AWS"
                name        = "AWSManagedRulesSQLiRuleSet"
            }
        }
        visibility_config {
            cloudwatch_metrics_enabled = true
            metric_name                = "${aws_wafv2_web_acl.fam_waf_api_gateway.name}-AWSManagedRulesSQLiRuleSet"
            sampled_requests_enabled   = true
        }
    }

    tags = {
        env = "${var.target_env}"
        managed-by = "terraform"
    }

    visibility_config {
        cloudwatch_metrics_enabled = true
        metric_name                = "${aws_wafv2_web_acl.fam_waf_api_gateway.name}"
        sampled_requests_enabled   = true
    }
}

# Cognito WAF ACL
resource "aws_wafv2_web_acl" "fam_waf_cognito" {
    name        = "${web_acl_name_prefix}-cognito"
    description = "Cognito WAF Rules"
    scope       = "REGIONAL"

    default_action {
        allow {}
    }


    ## AWS Managed rules below.
    /*
       Not like API-Gateway rules, following rules are ignored for now
       because it prevents access from outside of Canada
       (block our team members' access)
       - Core rule set (AWS-AWSManagedRulesCommonRuleSet)
       - SQL database (AWS-AWSManagedRulesSQLiRuleSet)
    */
    rule {
        name     = "AWS-AWSManagedRulesAmazonIpReputationList"
        priority = 0

        override_action {
            none {}
        }
        statement {
            managed_rule_group_statement {
                vendor_name = "AWS"
                name        = "AWSManagedRulesAmazonIpReputationList"
            }
        }
        visibility_config {
            cloudwatch_metrics_enabled = true
            metric_name                = "${aws_wafv2_web_acl.fam_waf_cognito.name}-AWSManagedRulesAmazonIpReputationList"
            sampled_requests_enabled   = true
        }
    }

    rule {
        name     = "AWS-AWSManagedRulesKnownBadInputsRuleSet"
        priority = 1

        override_action {
            none {}
        }
        statement {
            managed_rule_group_statement {
                vendor_name = "AWS"
                name        = "AWSManagedRulesKnownBadInputsRuleSet"
            }
        }
        visibility_config {
            cloudwatch_metrics_enabled = true
            metric_name                = "${aws_wafv2_web_acl.fam_waf_cognito.name}-AWSManagedRulesKnownBadInputsRuleSet"
            sampled_requests_enabled   = true
        }
    }

    rule {
        name     = "AWS-AWSManagedRulesLinuxRuleSet"
        priority = 2

        override_action {
            none {}
        }
        statement {
            managed_rule_group_statement {
                vendor_name = "AWS"
                name        = "AWSManagedRulesLinuxRuleSet"
            }
        }
        visibility_config {
            cloudwatch_metrics_enabled = true
            metric_name                = "${aws_wafv2_web_acl.fam_waf_cognito.name}-AWSManagedRulesLinuxRuleSet"
            sampled_requests_enabled   = true
        }
    }

    tags = {
        env = "${var.target_env}"
        managed-by = "terraform"
    }

    visibility_config {
        cloudwatch_metrics_enabled = true
        metric_name                = "${aws_wafv2_web_acl.fam_waf_cognito.name}"
        sampled_requests_enabled   = true
    }
}

# CloudFront WAF ACL
resource "aws_wafv2_web_acl" "fam_waf_cloudfront" {
    name        = "${web_acl_name_prefix}-cloudfront"
    description = "CloudFront WAF Rules"
    scope       = "CLOUDFRONT"

    default_action {
        allow {}
    }


    ## AWS Managed rules below.
    rule {
        name     = "AWS-AWSManagedRulesAmazonIpReputationList"
        priority = 0

        override_action {
            none {}
        }
        statement {
            managed_rule_group_statement {
                vendor_name = "AWS"
                name        = "AWSManagedRulesAmazonIpReputationList"
            }
        }
        visibility_config {
            cloudwatch_metrics_enabled = true
            metric_name                = "${aws_wafv2_web_acl.fam_waf_cloudfront.name}-AWSManagedRulesAmazonIpReputationList"
            sampled_requests_enabled   = true
        }
    }

    rule {
        name     = "AWS-AWSManagedRulesCommonRuleSet"
        priority = 1

        override_action {
            none {}
        }
        statement {
            managed_rule_group_statement {
                vendor_name = "AWS"
                name        = "AWSManagedRulesCommonRuleSet"
            }
        }
        visibility_config {
            cloudwatch_metrics_enabled = true
            metric_name                = "${aws_wafv2_web_acl.fam_waf_cloudfront.name}-AWSManagedRulesCommonRuleSet"
            sampled_requests_enabled   = true
        }
    }

    rule {
        name     = "AWS-AWSManagedRulesKnownBadInputsRuleSet"
        priority = 2

        override_action {
            none {}
        }
        statement {
            managed_rule_group_statement {
                vendor_name = "AWS"
                name        = "AWSManagedRulesKnownBadInputsRuleSet"
            }
        }
        visibility_config {
            cloudwatch_metrics_enabled = true
            metric_name                = "${aws_wafv2_web_acl.fam_waf_cloudfront.name}-AWSManagedRulesKnownBadInputsRuleSet"
            sampled_requests_enabled   = true
        }
    }

    rule {
        name     = "AWS-AWSManagedRulesLinuxRuleSet"
        priority = 3

        override_action {
            none {}
        }
        statement {
            managed_rule_group_statement {
                vendor_name = "AWS"
                name        = "AWSManagedRulesLinuxRuleSet"
            }
        }
        visibility_config {
            cloudwatch_metrics_enabled = true
            metric_name                = "${aws_wafv2_web_acl.fam_waf_cloudfront.name}-AWSManagedRulesLinuxRuleSet"
            sampled_requests_enabled   = true
        }
    }

    rule {
        name     = "AWS-AWSManagedRulesSQLiRuleSet"
        priority = 4

        override_action {
            none {}
        }
        statement {
            managed_rule_group_statement {
                vendor_name = "AWS"
                name        = "AWSManagedRulesSQLiRuleSet"
            }
        }
        visibility_config {
            cloudwatch_metrics_enabled = true
            metric_name                = "${aws_wafv2_web_acl.fam_waf_cloudfront.name}-AWSManagedRulesSQLiRuleSet"
            sampled_requests_enabled   = true
        }
    }

    tags = {
        env = "${var.target_env}"
        managed-by = "terraform"
    }

    visibility_config {
        cloudwatch_metrics_enabled = true
        metric_name                = "${aws_wafv2_web_acl.fam_waf_cloudfront.name}"
        sampled_requests_enabled   = true
    }
}