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

# TODO: Only uses this before forest-client api integration from front-end.
DUMMY_FOREST_CLIENT_NAME = "DUMMY_FOREST_CLIENT_NAME"
