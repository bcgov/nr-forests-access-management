
# User Type
from enum import Enum


class UserType(str, Enum):
    IDIR = 'IDIR'
    BCEID = 'BCeID'


FAM_SYSTEM_USER = 'FAM_SYSTEM_USER'  # TODO: check what user to use later when login user OIDC token is known.
DUMMY_FOREST_CLIENT_NAME = 'DUMMY_FOREST_CLIENT_NAME'  # TODO: Only uses this before forest-client api integration from fronte-end.