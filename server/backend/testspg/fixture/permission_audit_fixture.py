import datetime
from api.app.constants import (
    PrivilegeDetailsPermissionTypeEnum,
    PrivilegeDetailsScopeTypeEnum,
)
from api.app.models.model import FamPrivilegeChangeAudit
from api.app.schemas import PermissionAuditHistoryResDto

USER_ID_1 = 1
USER_ID_2 = 2
APPLICATION_ID_1 = 1
APPLICATION_ID_2 = 2
CHANGE_DATE_1 = datetime.datetime(2024, 9, 10, 0, 0)
CHANGE_DATE_2 = datetime.datetime(2024, 9, 11, 0, 0)
ENDPOINT_ROOT = "/permission-audit-history"

PERFORMER_DETAILS_1 = {
    "username": "bigfoot_hunter",
    "first_name": "Sasquatch",
    "last_name": "Seeker",
    "email": "sasquatch.seeker@cryptid.com",
}

PERFORMER_DETAILS_2 = {
    "username": "big_monke",
    "first_name": "Rainbow",
    "last_name": "Winton",
    "email": "rainbow.winton@zooworld.com",
}

PRIVILEGE_DETAILS = {
    "permission_type": PrivilegeDetailsPermissionTypeEnum.END_USER,
    "roles": [
        {
            "role": "submitter",
            "scopes": [
                {
                    "scope_type": PrivilegeDetailsScopeTypeEnum.CLIENT,
                    "client_id": "00001024",
                    "client_name": "Chop Trees Inc",
                }
            ],
        }
    ],
}

AUDIT_RECORD_1 = FamPrivilegeChangeAudit(
    change_date=CHANGE_DATE_1,
    change_performer_user_details=PERFORMER_DETAILS_1,
    change_performer_user_id=USER_ID_1,
    change_target_user_id=USER_ID_1,
    create_date=CHANGE_DATE_1,
    create_user="admin",
    privilege_change_type_code="GRANT",
    privilege_details=PRIVILEGE_DETAILS,
    application_id=APPLICATION_ID_1,
)

AUDIT_RECORD_2 = FamPrivilegeChangeAudit(
    change_date=CHANGE_DATE_2,
    change_performer_user_details=PERFORMER_DETAILS_2,
    change_performer_user_id=USER_ID_2,
    change_target_user_id=USER_ID_2,
    create_date=CHANGE_DATE_2,
    create_user="admin",
    privilege_change_type_code="REVOKE",
    privilege_details=PRIVILEGE_DETAILS,
    application_id=APPLICATION_ID_1,
)

AUDIT_RECORD_3 = FamPrivilegeChangeAudit(
    change_date=CHANGE_DATE_2,
    change_performer_user_details=PERFORMER_DETAILS_1,
    change_performer_user_id=USER_ID_1,
    change_target_user_id=USER_ID_1,
    create_date=CHANGE_DATE_2,
    create_user="admin",
    privilege_change_type_code="REVOKE",
    privilege_details=PRIVILEGE_DETAILS,
    application_id=APPLICATION_ID_2,
)

MOCKED_PERMISSION_HISTORY_RESPONSE = [
    PermissionAuditHistoryResDto(
        change_date=CHANGE_DATE_1,
        change_performer_user_details=PERFORMER_DETAILS_1,
        change_performer_user_id=1,
        change_target_user_id=1,
        create_date=CHANGE_DATE_1,
        create_user="admin",
        privilege_change_type_code="GRANT",
        privilege_details=PRIVILEGE_DETAILS,
    )
]
