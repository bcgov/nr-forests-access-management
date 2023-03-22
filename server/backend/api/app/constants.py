# User Type
from enum import Enum


class UserType(str, Enum):
    IDIR = "I"
    BCEID = "B"


class RoleType(str, Enum):
    ROLE_TYPE_ABSTRACT = "A"
    ROLE_TYPE_CONCRETE = "C"


class AppEnv(str, Enum):
    APP_ENV_TYPE_DEV = "DEV"
    APP_ENV_TYPE_TEST = "TEST"
    APP_ENV_TYPE_PROD = "PROD"


FAM_PROXY_API_USER = "fam_proxy_api"

COGNITO_USERNAME_KEY = "username"

FOM_SUBMITTER_ROLE_NAME = "FOM_Submitter"
FOM_APP_DESC = "Forest Operations Map"
FOM_ROLE_PURPOSE = "Grant a user access to submit to FOM"
FOM_APP_DEV_NAME = "fom_dev"
FOM_APP_TEST_NAME = "fom_test"

# TODO: Only uses this before forest-client api integration from front-end.
DUMMY_FOREST_CLIENT_NAME = "DUMMY_FOREST_CLIENT_NAME"
