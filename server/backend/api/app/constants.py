# User Type
from enum import Enum


class UserType(str, Enum):
    IDIR = "I"
    BCEID = "B"


class RoleType(str, Enum):
    ROLE_TYPE_ABSTRACT = "A"
    ROLE_TYPE_CONCRETE = "C"


FAM_PROXY_API_USER = "fam_proxy_api"

# TODO: Only uses this before forest-client api integration from front-end.
DUMMY_FOREST_CLIENT_NAME = "DUMMY_FOREST_CLIENT_NAME"
