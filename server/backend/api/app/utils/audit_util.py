import logging
from enum import Enum
import json
from api.app.models import model as models
from api.app.schemas import Requester
from fastapi import Request, HTTPException


LOGGER = logging.getLogger(__name__)


class AuditEventType(str, Enum):
    CREATE_USER_ROLE_ACCESS = "Grant User Role(S) Access"
    REMOVE_USER_ROLE_ACCESS = "Remove User Role(S) Access"


class AuditEventOutcome(str, Enum):
    SUCCESS = 1
    FAIL = 0


class AuditEventLog:
    request: Request
    event_type: AuditEventType
    event_outcome: AuditEventOutcome
    application: models.FamApplication
    role: models.FamRole
    forest_client_number: str
    requesting_user: Requester
    target_user: models.FamUser
    exception: Exception

    def __init__(
        self,
        request: Request = None,
        event_type: AuditEventType = None,
        event_outcome: AuditEventOutcome = None,
        application: models.FamApplication = None,
        role: models.FamRole = None,
        forest_client_number: str = None,
        requesting_user: Requester = None,
        target_user: models.FamUser = None,
        exception: Exception = None,
    ):
        self.request = request
        self.event_type = event_type
        self.event_outcome = event_outcome
        self.application = application
        self.role = role
        self.forest_client_number = forest_client_number
        self.requesting_user = requesting_user
        self.target_user = target_user
        self.exception = exception

    def log_event(self):

        log_item = {
            "auditEventTypeCode": self.event_type.name if self.event_type else None,
            "auditEventResultCode": self.event_outcome.name
            if self.event_outcome
            else None,
            "applicationId": self.application.application_id
            if self.application
            else None,
            "applicationName": self.application.application_name
            if self.application
            else None,
            "applicationEnv": self.application.app_environment
            if self.application
            else None,
            "roleId": self.role.role_id if self.role else None,
            "roleName": self.role.role_name if self.role else None,
            "roleType": self.role.role_type_code if self.role else None,
            "forestClientNumber": self.forest_client_number,
            "targetUser": {
                "userGuid": self.target_user.user_guid if self.target_user else None,
                "userType": self.target_user.user_type_code
                if self.target_user
                else None,
                "idpUserName": self.target_user.user_name if self.target_user else None,
                "cognitoUsername": self.target_user.cognito_user_id
                if self.target_user
                else None,
            },
            "requestingUser": {
                "userGuid": self.requesting_user.user_guid
                if self.requesting_user
                else None,
                "userType": self.requesting_user.user_type_code
                if self.requesting_user
                else None,
                "idpUserName": self.requesting_user.user_name
                if self.requesting_user
                else None,
                "cognitoUsername": self.requesting_user.cognito_user_id
                if self.requesting_user
                else None,
            },
            "requestIP": self.request.client.host if self.request.client else "unknown",
        }

        if self.exception:
            if type(self.exception) == HTTPException:
                log_item["exception"] = {
                    "exceptionType": "HTTPException",
                    "statusCode": self.exception.status_code,
                    "details": self.exception.detail,
                }

        LOGGER.info(json.dumps(log_item))
