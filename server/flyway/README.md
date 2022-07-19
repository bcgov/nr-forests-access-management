# Database Migration Management
Using the [flyway-lambda](https://github.com/Geekoosh/flyway-lambda) open source project to manage database migrations using Terraform.

* The file /flyway/lambda/flyway-all.jar was downloaded from github (wget https://github.com/Geekoosh/flyway-lambda/releases/download/v0.8/flyway-all.jar)
* Terraform configurations for deploying the lambda are in /server/db-migration.tf
* Terraform configurations for executing the lambda are in /flyway/flyway-invoke.tf (separated to keep it out of "terraform plan")
* SQL Scripts live in /flyway/db-migrations
* The lambda can be run from the command-line (for rollbacks if necessary)
* The lambda is pre-configured to use AWS Secrets to get username and password to connect to the DB
* UNDO is not a supported flyway operation

The following commands can be used to invoke flyway lambda from aws cli. You need to "click for credentials" first!
You also have to make sure the paths and the db connection string in request.json are correct.
Also, if you look in flyway-invoke.tf, you will notice that there are replacements for the V1 migration. If you are invoking that migration, you will need to (temporarily)

PAYLOAD=$(cat /home/conrad/repos/nr-forests-access-management/flyway/request.json | base64)
aws lambda invoke --function-name lambda-db-migrations --payload $PAYLOAD out.json
cat out.json