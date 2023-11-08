# Notes on setup to help debug/ terraform on AWS / SEA locally

# Note: instructions with *Terragrunt* coming soon!

<img src="https://lh3.googleusercontent.com/pw/AL9nZEUdGiRiLkDzqzut5LaPh7wE7yhuJtqLB4X_ofDBR329pgzUnL-FMAHUC1pYIRX9NUOcJPW-mROg9KK0NYkptnZMtlkO0T-XmdeyWixD9cN4uSDThxhEWrmEDs5HgEdRvnet0KtS-lK30HsuuIWElHFGSQ=w1300-h732-no?authuser=0" width="700px">

# Setup for running Locally

## Connect to AWS

* [Login to AWS](https://oidc.gov.bc.ca/auth/realms/umafubc9/protocol/saml/clients/amazon-aws)
* copy the AWS creds to a terminal
* run this line to get terraform token

`aws ssm get-parameter --name "/octk/tfc/team-token" --with-decryption | jq -r '.Parameter.Value'`

* copy the parameter into ~/.terraformrc

```
credentials "app.terraform.io" {
    token = "terraform-token-goes-here"
}
```

# Create local backend.hcl

* create this file and populate with the following:
```
organization = "bcgov"
workspaces {
    name = "<license plate>-<env>-backend"
}
```

# Create a github.auto.tfvars file

```
organization = "bcgov"
oidc_idir_dev_idp_client_id = "dummy"
oidc_idir_dev_idp_client_secret = "dummy"
oidc_idir_dev_idp_issuer = "dummy"
oidc_bceid_business_dev_idp_client_secret = "dummy"
oidc_bceid_business_dev_idp_client_id = "dummy"
oidc_bceid_business_dev_idp_issuer = "dummy"
db_cluster_snapshot_identifier = "pre-flyway-<githubbranch>-<commitid>"
```

## Check the format of the config

`terraform fmt`

## Run Terraform init

init the directory:

`terraform init -backend-config=backend.hcl`

## Validate the config

`terraform validate`

## Run Terraform plan to test existing config

[docs on refresh option](https://www.terraform.io/cli/commands/plan#refresh-false)

`terraform plan -refresh=false`



# Terraform Deploy via API - DIDN'T FIGURE THIS OUT - NOT WORKING

terraform cloud via local script

### Set Variables

``` bash
export TOKEN=<token>
export WORKSPACE_NAME=<AWS namespace>
export ORG_NAME=bcgov
```

### create upload package

``` bash
cd server
UPLOAD_FILE_NAME="./content-$(date +%s).tar.gz"
tar \
--exclude='./backend/venv' \
--exclude='./backend/tests' \
--exclude='./backend/.env' \
--exclude='.env' \
--exclude='./fam_api' \
--exclude='./.terraform.lock.hcl' \
--exclude='./fam_auth_function.zip' \
--exclude='./fam-ui-api.zip' \
--exclude='./fam-ui-user-management-api.zip' \
--exclude='./github.auto.tfvars' \
--exclude='localtest.auto.tfvars' \
-zcvf "$UPLOAD_FILE_NAME" -C "$CONTENT_DIRECTORY" .
```

### get workspace id

``` bash
WORKSPACE_ID=($(curl \
  --header "Authorization: Bearer $TOKEN" \
  --header "Content-Type: application/vnd.api+json" \
  https://app.terraform.io/api/v2/organizations/$ORG_NAME/workspaces/$WORKSPACE_NAME \
  | jq -r '.data.id')) && echo $WORKSPACE_ID
```

### Create config version, and get upload url

``` bash
echo '{"data":{"type":"configuration-versions"}}' > ./create_config_version.json
UPLOAD_URL=($(curl \
  --header "Authorization: Bearer $TOKEN" \
  --header "Content-Type: application/vnd.api+json" \
  --request POST \
  --data @create_config_version.json \
  https://app.terraform.io/api/v2/workspaces/$WORKSPACE_ID/configuration-versions \
  | jq -r '.data.attributes."upload-url"'))
```

* didn't get this ^^ step working

  ### Next....

  Was working on instructions provided here:
  https://www.terraform.io/cloud-docs/run/api
