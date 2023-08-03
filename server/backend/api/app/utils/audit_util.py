import logging
from enum import Enum
from typing import Optional

from fastapi import Request
from pydantic import BaseModel

from api.requester import Requester
from api.app.constants import AppEnv

LOGGER = logging.getLogger(__name__)

LOGGING_TYPE_AUDIT = "Audit" # 'Audit' type of logging.

# EVENT related audit constants.
class AuditEvent(str, Enum):
    CREATE_USER_ROLE_ACCESS = "Grant User Role(S) Access" # Create
    REMOVE_USER_ROLE_ACCESS = "Remove User Role(S) Access" # Delete

# EVENT OUTCOME related audit constants.
class AuditEventOutcome(str, Enum):
    SUCCESS = "Success" # Meaning: action 'Success' or 'Granted'.
    FAIL = "Fail" # Meaning:

# Audit helper schema class below.
class AuditTarget(BaseModel):
    user: Optional[Requester] # Target user.
    application_id: Optional[int]
    application_name: Optional[str]
    app_environment: Optional[AppEnv]

    forest_client_number: Optional[str]


def audit_log(
        request: Request,
        requestor: Requester,
        event: AuditEvent,
        outcome: AuditEventOutcome,
        target: AuditTarget = None
):
    LOGGER.info(
        f"type={LOGGING_TYPE_AUDIT}, "
        f"event={event.value}, "
        f"requestor=({requestor} IP={request.client}), "
        f"target=({target})",
        f"outcome={outcome.value}"
    )