from enum import Enum
from typing import TypeVar

# ----------------------- Generic Type Variable Declaration ----------------------- #
T = TypeVar('T')

# --------------------------------- Schema Enums --------------------------------- #
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

class IdimSearchUserParamType(str, Enum):
    USER_GUID = "userGuid"
    USER_ID = "userId"

class EmailSendingStatus(str, Enum):
    NOT_REQUIRED = "NOT_REQUIRED"  # does not require sending email.
    SENT_TO_EMAIL_SERVICE_SUCCESS = "SENT_TO_EMAIL_SERVICE_SUCCESS"  # send to external service successful.
    SENT_TO_EMAIL_SERVICE_FAILURE = "SENT_TO_EMAIL_SERVICE_FAILURE"  # technical/validation failure during sending to external service.

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

class PrivilegeChangeTypeEnum(str, Enum):
    GRANT = "GRANT"
    REVOKE = "REVOKE"
    UPDATE = "UPDATE"

class SortOrderEnum(str, Enum):
    ASC = "asc"
    DESC = "desc"

class DelegatedAdminSortByEnum(str, Enum):
    # Note: this is not the exact model column name, requires table column mapping.
    CREATE_DATE = "create_date"  # first one is the default sort field
    USER_NAME = "user_name"
    DOMAIN = "user_type_code"
    EMAIL = "email"
    FULL_NAME = "full_name"  # special case: first_name + last_name
    ROLE_DISPLAY_NAME = "role_display_name"
    FOREST_CLIENT_NUMBER = "forest_client_number"

# ------------------------------- Schema Constants ------------------------------- #
APPLICATION_FAM = "FAM"
COGNITO_USERNAME_KEY = "username"

FOREST_CLIENT_STATUS = {"KEY": "clientStatusCode", "CODE_ACTIVE": "ACT"}

IDIM_PROXY_ACCOUNT_TYPE_MAP = {UserType.IDIR: "Internal", UserType.BCEID: "Business"}

SYSTEM_ACCOUNT_NAME = "system"
USER_NAME_MAX_LEN = 20
USER_NAME_MIN_LEN = 2
FIRST_NAME_MAX_LEN = 50
LAST_NAME_MAX_LEN = 50
EMAIL_MAX_LEN = 250
ROLE_NAME_MAX_LEN = 100
CLIENT_NUMBER_MAX_LEN = 8
CLIENT_NAME_MAX_LEN = 60
APPLICATION_DESC_MAX_LEN = 200
CREATE_USER_MAX_LEN = 100
MIN_PAGE = 1
DEFAULT_PAGE_SIZE = 50
MIN_PAGE_SIZE = 10

# The intent is  to have "max=100" per page, however frontend is not ready, so if need to return "all records" found
# and let frontend do the pagination, we could set it to 100000.
# >> MAX_PAGE_SIZE = 100
MAX_PAGE_SIZE = 100000
SEARCH_FIELD_MIN_LENGTH = 3
SEARCH_FIELD_MAX_LENGTH = 30

# ------- Error/Exception Code Constant -------

# Note, this is default error code but better use specific code category if possible.
ERROR_CODE_INVALID_OPERATION = "invalid_operation"
ERROR_CODE_INVALID_REQUEST_PARAMETER = "invalid_request_parameter"
ERROR_CODE_MISSING_KEY_ATTRIBUTE = "missing_key_attribute"
ERROR_CODE_UNKNOWN_STATE = "unknown_state"
