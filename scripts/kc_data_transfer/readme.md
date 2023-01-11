# Overview

Scripts in this directory exist to copy the Authorization that is used by FOM,
from keycloak, to FAM.  At a high level the script will:

1. extracts/reads the roles that have been entered into keycloak for the FOM application
1. filters the roles to include only forest client related roles
1. for each forest client role, creates a corresponding role in FAM, if it doesn't already exist
1. Retrieves the users who are members of the current keycloak role
1. Calls the FAM user / role assignment end point to add the user to the equivalent
    fam role

# Script setup

The following is the instruction required to setup the script to run.  The script
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
python3.8 -m venv venv
. ./venv/bin/activate
pip install -r src/requirements.txt
```

## Populate the following environment variables

Either set these env vars or stuff them into .env file.  If the .env file
exists in the ./scripts/kc_data_transfer directory it will automatically
get loaded by the code.

* KC_HOST - url to keycloak instance, ex: https://mykeycloak.ca
* KC_CLIENTID - The client id that has been configured as a service account
* KC_SECRET - The secret for the above client
* KC_REALM=ichqx89w
* KC_FOM_CLIENTID=the name of the client used for fom

## Run the script

```
python src/KeyCloakTransfer.py
```

## Future - Using after API security is added

Once security is implemented in FAM, an API client and secret will have to be
used to access the FAM api.  The client/secret will likely then be used to
retrieve an access token.  The logic for how to do this is likely the same as
the logic used in the `KeyCloak.py` module.
