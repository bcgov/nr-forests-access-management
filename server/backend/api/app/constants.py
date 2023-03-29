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


class FamForestClientStatusType(str, Enum):
    ACTIVE = "A"
    INACTIVE = "I"


FOREST_CLIENT_STATUS = {
    "KEY": "clientStatusCode",
    "CODE_ACTIVE": "ACT"
}

FAM_PROXY_API_USER = "fam_proxy_api"

COGNITO_USERNAME_KEY = "username"
