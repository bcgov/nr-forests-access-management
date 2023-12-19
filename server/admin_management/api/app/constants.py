from enum import Enum


class AppEnv(str, Enum):
    APP_ENV_TYPE_DEV = "DEV"
    APP_ENV_TYPE_TEST = "TEST"
    APP_ENV_TYPE_PROD = "PROD"


class UserType(str, Enum):
    IDIR = "I"
    BCEID = "B"


COGNITO_USERNAME_KEY = "username"