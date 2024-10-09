import datetime

from api.app.constants import (PrivilegeChangeTypeEnum,
                               PrivilegeDetailsPermissionTypeEnum,
                               PrivilegeDetailsScopeTypeEnum)
from api.app.models.model import FamPrivilegeChangeAudit
from api.app.schemas import (PermissionAuditHistoryRes,
                             PrivilegeChangePerformerSchema,
                             PrivilegeDetailsSchema)
from testspg.constants import (FAM_APPLICATION_ID, FOM_DEV_APPLICATION_ID,
                               TEST_USER_ID)

USER_ID_1 = TEST_USER_ID
USER_ID_2 = 2
APPLICATION_ID_1 = FAM_APPLICATION_ID
APPLICATION_ID_2 = FOM_DEV_APPLICATION_ID
CHANGE_DATE_1 = datetime.datetime(2024, 9, 10, 0, 0)
CHANGE_DATE_2 = datetime.datetime(2024, 9, 11, 0, 0)
ENDPOINT_ROOT = "/permission-audit-history"

PERFORMER_DETAILS_1 = PrivilegeChangePerformerSchema(
    username="bigfoot_hunter",
    first_name="Sasquatch",
    last_name="Seeker",
    email="sasquatch.seeker@cryptid.com",
).model_dump()

PERFORMER_DETAILS_2 = PrivilegeChangePerformerSchema(
    username="big_monke",
    first_name="Rainbow",
    last_name="Winton",
    email="rainbow.winton@zooworld.com",
).model_dump()

PRIVILEGE_DETAILS = PrivilegeDetailsSchema(
    permission_type=PrivilegeDetailsPermissionTypeEnum.END_USER,
    roles=[
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
).model_dump()

AUDIT_RECORD_U1_A1_D1 = FamPrivilegeChangeAudit(
    privilege_change_audit_id=1,
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

# Same as AUDIT_RECORD_U1_A1_D1 but with different dates
AUDIT_RECORD_U1_A1_D2 = FamPrivilegeChangeAudit(
    privilege_change_audit_id=2,
    change_date=CHANGE_DATE_2,
    change_performer_user_details=PERFORMER_DETAILS_1,
    change_performer_user_id=USER_ID_1,
    change_target_user_id=USER_ID_1,
    create_date=CHANGE_DATE_2,
    create_user="admin",
    privilege_change_type_code=PrivilegeChangeTypeEnum.REVOKE,
    privilege_details=PRIVILEGE_DETAILS,
    application_id=APPLICATION_ID_1,
)

AUDIT_RECORD_U1_A2 = FamPrivilegeChangeAudit(
    privilege_change_audit_id=3,
    change_date=CHANGE_DATE_2,
    change_performer_user_details=PERFORMER_DETAILS_1,
    change_performer_user_id=USER_ID_1,
    change_target_user_id=USER_ID_1,
    create_date=CHANGE_DATE_2,
    create_user="admin",
    privilege_change_type_code=PrivilegeChangeTypeEnum.REVOKE,
    privilege_details=PRIVILEGE_DETAILS,
    application_id=APPLICATION_ID_2,
)

AUDIT_RECORD_U2_A2 = FamPrivilegeChangeAudit(
    privilege_change_audit_id=4,
    change_date=CHANGE_DATE_2,
    change_performer_user_details=PERFORMER_DETAILS_2,
    change_performer_user_id=USER_ID_2,
    change_target_user_id=USER_ID_2,
    create_date=CHANGE_DATE_2,
    create_user="admin",
    privilege_change_type_code=PrivilegeChangeTypeEnum.REVOKE,
    privilege_details=PRIVILEGE_DETAILS,
    application_id=APPLICATION_ID_2,
)

MOCKED_PERMISSION_HISTORY_RESPONSE = [
    PermissionAuditHistoryRes(
        privilege_change_audit_id=1,
        change_date=CHANGE_DATE_1,
        change_performer_user_details=PERFORMER_DETAILS_1,
        change_performer_user_id=1,
        change_target_user_id=1,
        create_date=CHANGE_DATE_1,
        create_user="admin",
        privilege_change_type_code="GRANT",
        privilege_details=PRIVILEGE_DETAILS,
        privilege_change_type_description="Role added",
    )
]
