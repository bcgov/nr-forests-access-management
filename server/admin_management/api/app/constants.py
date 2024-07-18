from enum import Enum

APPLICATION_FAM = "FAM"
COGNITO_USERNAME_KEY = "username"


class AppEnv(str, Enum):
    APP_ENV_TYPE_DEV = "DEV"
    APP_ENV_TYPE_TEST = "TEST"
    APP_ENV_TYPE_PROD = "PROD"


class ApiInstanceEnv(str, Enum):
    # Environment constant for connecting to external API.
    # The integration with external API only has TEST or PROD on API instance.
    TEST = "TEST"
    PROD = "PROD"


class AwsTargetEnv(str, Enum):
    # "target_env" only exists on AWS (Injected from Gov AWS platform), for FAM.
    # It is lower case. Locally it does not need this.
    # Not to be confused with application environment or API instance environment.
    DEV = "dev"
    TEST = "test"
    PROD = "Prod"


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

IDIM_PROXY_ACCOUNT_TYPE_MAP = {UserType.IDIR: "Internal", UserType.BCEID: "Business"}


class IdimSearchUserParamType(str, Enum):
    USER_GUID = "userGuid"
    USER_ID = "userId"


# ------- Error/Exception Code Constant -------

# Note, this is default error code but better use specific code category if possible.
ERROR_CODE_INVALID_OPERATION = "invalid_operation"
ERROR_CODE_INVALID_REQUEST_PARAMETER = "invalid_request_parameter"
ERROR_CODE_MISSING_KEY_ATTRIBUTE = "missing_key_attribute"
