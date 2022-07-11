# Database Migration Management
Using the [flyway-lambda](https://github.com/Geekoosh/flyway-lambda) open source project to manage database migrations using Terraform.

* The file /flyway/lambda/flyway-all.jar was downloaded from github (wget https://github.com/Geekoosh/flyway-lambda/releases/download/v0.8/flyway-all.jar)
* Terraform configurations for deploying the lambda are in /server/db-migration.tf
* Terraform configurations for executing the lambda are in /flyway/flyway-invoke.tf (separated to keep it out of "terraform plan")
* SQL Scripts live in /flyway/db-migrations
* The lambda can be run from the command-line (for rollbacks if necessary)