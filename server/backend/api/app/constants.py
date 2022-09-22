
# User Type
from enum import Enum


class UserType(str, Enum):
    IDIR = 'IDIR'
    BCEID = 'BCeID'


FAM_PROXY_API_USER = 'fam_proxy_api'
DUMMY_FOREST_CLIENT_NAME = 'DUMMY_FOREST_CLIENT_NAME'  # TODO: Only uses this before forest-client api integration from fronte-end.
FOREST_CLIENT_ID_PADDING = {'char': '0', 'length': 8}  # padding style, default to the left.
