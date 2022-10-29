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

# Local Development

The Dockerfile in this directory can be run (optionally from docker-compose at the root of the project). The resulting docker container has flyway installed and all the scripts copied over. The scripts can be applied to the database with the following command from your terminal:

docker exec -it famdb flyway-migrate.sh

Note: it would have been lovely to put that script into /docker-entrypoint-initdb.d and get it to run on startup of the DB, but flyway needs to connect over TCP/IP and Postgres doesn't expose TCP/IP until after startup (as per https://github.com/docker-library/postgres/pull/440). 