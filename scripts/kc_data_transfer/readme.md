# Overview

Scripts in this directory exist to copy the AuthZ data for FOM out of keycloak
to FAM.  The script will:

1. extracts roles that have been entered in keycloak for the FOM application
1. creates a corresponding role in FAM, if it doesn't already exist
1. for each keycloak role, retrieves the users who are members of that role
1. checks to see if the users already exist in fam
1. if they do not add the user role assignment for fam

# Script setup

KeyCloakToFAM.fam_fom_abstract_role_name = the abstract role name that forest client
    concrete roles are related to.

## create and invoke virtual environment

```
cd scripts/kc_data_transfer/
python3.8 -m venv venv
. ./venv/bin/activate
pip install -r src/requirements.txt
```

## Populate the following environment variables

* KC_HOST - url to keycloak instance, ex: https://mykeycloak.ca
* KC_CLIENTID - The client id that has been configured as a service account
* KC_SECRET - The secret for the above client
* KC_REALM=ichqx89w
* KC_FOM_CLIENTID=the name of the client used for fom

## Run the script

```
python src/KeyCloakTransfer.py
```
