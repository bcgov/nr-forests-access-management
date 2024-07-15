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


# Internal defined enum client status constants for FAM 'router_forest_client'.
# ACTIVE/INACTIVE are mapped from Forest Client API spce.
# See schemas.py/FamForestClientStatus class.
class FamForestClientStatusType(str, Enum):
    ACTIVE = "A"
    INACTIVE = "I"


DESCRIPTION_ACTIVE = "Active"
DESCRIPTION_INACTIVE = "Inactive"

# Constans for FAM to coneniently refer to Forest Client API return json object
# keys/values.
FOREST_CLIENT_STATUS = {"KEY": "clientStatusCode", "CODE_ACTIVE": "ACT"}

FAM_PROXY_API_USER = "fam_proxy_api"

COGNITO_USERNAME_KEY = "username"

# The most current terms and conditions. Note, when terms and conditions gets updated
# at frontend, this also needs to be updated and in-sync.
CURRENT_TERMS_AND_CONDITIONS_VERSION = "1"

IDIM_PROXY_ACCOUNT_TYPE_MAP = {UserType.IDIR: "Internal", UserType.BCEID: "Business"}


class IdimSearchUserParamType(str, Enum):
    USER_GUID = "userGuid"
    USER_ID = "userId"


# ------- Error/Exception Code Constant -------

# Note, this is default error code but better use specific code category if possible.
ERROR_CODE_INVALID_OPERATION = "invalid_operation"
ERROR_CODE_INVALID_APPLICATION_ID = "invalid_application_id"
ERROR_CODE_SELF_GRANT_PROHIBITED = "self_grant_prohibited"
ERROR_CODE_INVALID_ROLE_ID = "invalid_role_id"
ERROR_CODE_REQUESTER_NOT_EXISTS = "requester_not_exists"
ERROR_CODE_EXTERNAL_USER_ACTION_PROHIBITED = "external_user_action_prohibited"
ERROR_CODE_DIFFERENT_ORG_GRANT_PROHIBITED = "different_org_grant_prohibited"
ERROR_CODE_MISSING_KEY_ATTRIBUTE = "missing_key_attribute"
ERROR_CODE_INVALID_REQUEST_PARAMETER = "invalid_request_parameter"
ERROR_CODE_TERMS_CONDITIONS_REQUIRED = "terms_condition_required"
