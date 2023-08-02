import logging


LOGGER = logging.getLogger(__name__)

LOGGING_TYPE_AUDIT = "Audit" # 'Audit' type of logging.

# EVENT related audit constants.
EVENT_CREATE_USER_ROLE_ACCESS = "Grant User Role(S) Access" # Create
EVENT_REMOVE_USER_ROLE_ACCESS = "Remove User Role(S) Access" # Delete

# EVENT OUTCOME related audit constants.
EVENT_OUTCOME_SUCCESS = "Success" # Meaning: action 'Success' or 'Granted'.
EVENT_OUTCOME_FAIL = "Fail" # Meaning: action 'Failed' or 'Rejected'.