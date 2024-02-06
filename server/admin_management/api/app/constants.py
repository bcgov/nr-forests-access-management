from enum import Enum

APPLICATION_FAM = "FAM"
COGNITO_USERNAME_KEY = "username"


class AppEnv(str, Enum):
    APP_ENV_TYPE_DEV = "DEV"
    APP_ENV_TYPE_TEST = "TEST"
    APP_ENV_TYPE_PROD = "PROD"


class UserType(str, Enum):
    IDIR = "I"
    BCEID = "B"


class RoleType(str, Enum):
    ROLE_TYPE_ABSTRACT = "A"
    ROLE_TYPE_CONCRETE = "C"


class FamForestClientStatusType(str, Enum):
    ACTIVE = "A"
    INACTIVE = "I"


class AdminRoleAuthGroup(str, Enum):
    """
    FAM data model does not explicitly have these role group of admins.
    However, business rules do differentiate purpose of admins as:
        (FAM_ADMIN, [APP]_ADMIN, DELEGATED_ADMIN)
    # Referencing to FAM confluence for design:
      https://apps.nrs.gov.bc.ca/int/confluence/display/FSAST1/Delegated+Access+Administration+Design (Auth Function)
    """

    FAM_ADMIN = "FAM_ADMIN"
    APP_ADMIN = "APP_ADMIN"
    DELEGATED_ADMIN = "DELEGATED_ADMIN"


FOREST_CLIENT_STATUS = {
    "KEY": "clientStatusCode",
    "CODE_ACTIVE": "ACT"
}
