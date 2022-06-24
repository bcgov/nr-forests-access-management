# Database Migration Management
Using the [flyway-lambda](https://github.com/Geekoosh/flyway-lambda) open source project to manage database migrations using Terraform.

* The file /server/db-migrations/lambda/flyway-0.0.4.zip was built from the [flyway-lambda](https://github.com/Geekoosh/flyway-lambda) project source code. 
* Terraform configurations for deploying the lambda are in /server/db-migration.tf
* The same Terraform file will execute the lambda as part of deploy
* SQL Scripts live in /server/db-migrations
* The lambda can be run from the command-line (for rollbacks if necessary)

