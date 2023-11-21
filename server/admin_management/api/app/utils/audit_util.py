import logging
from enum import Enum
import json
from api.app.models import model as models
from fastapi import Request, HTTPException


LOGGER = logging.getLogger(__name__)


class AuditEventType(str, Enum):
    CREATE_APPLICATION_ADMIN_ACCESS = "Grant User Application Admin Access"
    REMOVE_APPLICATION_ADMIN_ACCESS = "Remove User Application Admin Access"


class AuditEventOutcome(str, Enum):
    SUCCESS = 1
    FAIL = 0


class AuditEventLog:
    request: Request
    event_type: AuditEventType
    event_outcome: AuditEventOutcome
    application: models.FamApplication
    requesting_user: models.FamUser
    target_user: models.FamUser
    exception: Exception

    def __init__(
        self,
        request: Request = None,
        event_type: AuditEventType = None,
        event_outcome: AuditEventOutcome = None,
        application: models.FamApplication = None,
        requesting_user: models.FamUser = None,
        target_user: models.FamUser = None,
        exception: Exception = None,
    ):
        self.request = request
        self.event_type = event_type
        self.event_outcome = event_outcome
        self.application = application
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

        if self.exception and type(self.exception) == HTTPException:
            log_item["exception"] = {
                "exceptionType": "HTTPException",
                "statusCode": self.exception.status_code,
                "details": self.exception.detail,
            }

        LOGGER.info(json.dumps(log_item))
