from enum import Enum


class AppEnv(str, Enum):
    APP_ENV_TYPE_DEV = "DEV"
    APP_ENV_TYPE_TEST = "TEST"
    APP_ENV_TYPE_PROD = "PROD"


class UserType(str, Enum):
    IDIR = "I"
    BCEID = "B"


# For differentiating admins (FAM_ADMIN, [APP]_ADMIN, DELEGATED_ADMIN)
class AdminRoleGroup(str, Enum):
    FAM_ADMIN = "FAM_ADMIN"
    APP_ADMIN = "APP_ADMIN"
    DELEGATED_ADMIN = "DELEGATED_ADMIN"


COGNITO_USERNAME_KEY = "username"