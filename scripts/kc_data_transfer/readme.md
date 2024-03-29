# Overview

Scripts in this directory exist to copy the Authorization that is used by FOM,
from keycloak, to FAM. At a high level the script will:

1. extracts/reads the roles that have been entered into keycloak for the FOM application
1. filters the roles to exclude 2 test roles
1. Retrieves the users who are members of the each keycloak role
1. Calls the FAM user / role assignment end point to add the user to the equivalent
   fam role

# Script setup

The following is the instruction required to setup the script to run. The script
uses environment variables to make config/secrets available.

## Background / Configuration

Forest client based roles created by the script will currently have the folowing
naming pattern:

`FOM_SUBMITTER_<forest client number>`

Where `FOM_SUBMITTER` is the name of the parent abstract role to all
forest client roles. To change this modify the method `KeyCloakToFAM.get_fam_forest_client_role_name` in `KeyCloakTransfer.py`

## create and invoke virtual environment

```
cd scripts/kc_data_transfer/
python3 -m venv venv
. ./venv/bin/activate
pip install -r src/requirements.txt
```

## Populate the following environment variables

Either set these env vars or stuff them into .env file. If the .env file
exists in the ./scripts/kc_data_transfer directory it will automatically
get loaded by the code. Just copy the envExample file to .env and change the
values. **Do not check in the .env file with sercets.**

All variables start with "KC" are for transfering user from keycloak. For transfering user from csv file, use the last four variables.

-   KC_HOST - url to keycloak instance (e.g. https://oidc.gov.bc.ca)
-   KC_CLIENTID - The client id that has been configured as a service account
-   KC_SECRET - The secret for the above client
-   KC_REALM - (e.g. 'ichqx89w' for the NR custom realm)
-   KC_FOM_CLIENTID=the name of the client used for fom
-   FAM_JWT - Your JWT token (steal from the docs page after authenticating or from your browser, see the section below)
-   FAM_URL - Base FAM API url (e.g. https://7j9h7vm7ag.execute-api.ca-central-1.amazonaws.com/v1)
-   APP_NAME_IN_FAM - The name of the app in the FAM database (e.g. "FOM_DEV")
-   APP_USER_FILE_PATH - The csv file that stores all user information for the app

## Get the FAM_JWT token

-   **Make sure you have the admin access to the application you specified for the "APP_NAME_IN_FAM" variable in the .env file**
-   Go to our api website, the url can be found through AWS API Gateway -> Stages -> v1 -> Invoke URL, the url is the invoke url + "/v1/docs"
-   In our api website, click on the "Authorized" button, and then paste the client id (client id is the big bold string on the screen), then click "Authorize"
-   Click on the GET fam_applications api, and try to execute it. In the response section, it shows the curl command with the Bearer token, that's the token we want to use for the "FAM_JWT" variable in the .env file. If you grant yourself any new access, make sure to re-generate the token so it can include the new roles

## Run the script

```
// transfer data from keycloak
python3 src/KeyCloakTransfer.py

// transfer data from csv file
python3 src/CsvTransfer.py
```

**Note**:

-   If the execusion time for the script is longer than 5 mins, need to go Cognito "fam_console" application, and change the access token expiration to a longer time (by default it's 5 mins)
-   We only support csv file currently. When we export the received excel sheet into csv format, it should using the delimiter "," and encoding in "utf-8-sig". The csv file should include the following column names:
    -   User: in the format of "USERSTYPE\USERNAME", for example "IDIR\DGreen"
    -   Profile: this is the column for the role
    -   For Organization: in the format of "[forest_client_number] - [organization_name]", for example "12345678 - MINISTRY OF FORESTS"
-   The script is tested on python version 3.10.9
