# User Type
from enum import Enum
from typing import TypeVar

# FAM application name in database
APPLICATION_FAM = "FAM"


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


class ApiInstanceEnv(str, Enum):
    # Environment constant for connecting to external API (Forest Client API and IDIM Proxy API).
    # The integration with external API only has TEST or PROD on API instance.
    TEST = "TEST"
    PROD = "PROD"


class AwsTargetEnv(str, Enum):
    # "target_env" only exists on AWS (Injected from Gov AWS platform), for FAM web application.
    # It's lower case, Locally does not need this.
    # Not to be confused with application environment or API instance environment.
    DEV = "dev"
    TEST = "test"
    PROD = "prod"


# Internal defined enum client status constants for FAM 'router_forest_client'.
# ACTIVE/INACTIVE are mapped from Forest Client API spce.
# See schemas/fam_forest_client_status.py class.
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


class EmailSendingStatus(str, Enum):
    NOT_REQUIRED = "NOT_REQUIRED"  # does not require sending email.
    SENT_TO_EMAIL_SERVICE_SUCCESS = (
        "SENT_TO_EMAIL_SERVICE_SUCCESS"  # send to external service successful.
    )
    SENT_TO_EMAIL_SERVICE_FAILURE = "SENT_TO_EMAIL_SERVICE_FAILURE"  # technical/validation failure during sending to external service.


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
ERROR_CODE_UNKNOWN_STATE = "unknown_state"

# ------------------------------- Schema Constants ------------------------------- #
SYSTEM_ACCOUNT_NAME = "system"
USER_NAME_MAX_LEN = 20
FIRST_NAME_MAX_LEN = 50
LAST_NAME_MAX_LEN = 50
EMAIL_MAX_LEN = 250
CLIENT_NUMBER_MAX_LEN = 8
CLIENT_NAME_MAX_LEN = 60
ROLE_NAME_MAX_LEN = 100
APPLICATION_NAME_MAX_LEN = 100
APPLICATION_DESC_MAX_LEN = 200
CREATE_USER_MAX_LEN = 100
MIN_PAGE = 1
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100

# --------------------------------- Schema Enums --------------------------------- #
class PrivilegeChangeTypeEnum(str, Enum):
    GRANT = "GRANT"
    REVOKE = "REVOKE"
    UPDATE = "UPDATE"

# Note! There is an issue for openapi generator to generate an enum with only 1 constant.
# Since in future we plan to use "District", it is added (and can be used later) here
# so openapi can generate it with no prolbme but for now it is a holder.
class PrivilegeDetailsScopeTypeEnum(str, Enum):
    CLIENT = "Client"
    DISTRICT = "District"


class PrivilegeDetailsPermissionTypeEnum(str, Enum):
    END_USER = "End User"
    DELEGATED_ADMIN = "Delegated Admin"
    APPLICATION_ADMIN = "Application Admin"


# ----------------------- Generic Type Variable Declaration ----------------------- #
T = TypeVar('T')