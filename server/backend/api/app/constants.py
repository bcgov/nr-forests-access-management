
# User Type
from enum import Enum


class UserType(str, Enum):
    IDIR = 'IDIR'
    BCEID = 'BCeID'


FAM_PROXY_API_USER = 'fam_proxy_api'
DUMMY_FOREST_CLIENT_NAME = 'DUMMY_FOREST_CLIENT_NAME'  # TODO: Only uses this before forest-client api integration from fronte-end.
