from datetime import datetime
from zoneinfo import ZoneInfo
from http import HTTPStatus

from api.app.constants import UserType
from api.app.models.model import (FamApplication, FamForestClient, FamRole,
                                  FamUser, FamUserRoleXref)
from api.app.schemas.fam_application import FamApplicationSchema
from api.app.schemas.fam_application_user_role_assignment_get import \
    FamApplicationUserRoleAssignmentGetSchema
from api.app.schemas.fam_forest_client import FamForestClientSchema
from api.app.schemas.fam_role_min import FamRoleMinSchema
from api.app.schemas.fam_role_with_client import FamRoleWithClientSchema
from api.app.schemas.fam_user_info import FamUserInfoSchema
from api.app.schemas.fam_user_role_assignment_create_response import \
    FamUserRoleAssignmentCreateRes
from api.app.schemas.fam_user_type import FamUserTypeSchema
from api.app.schemas.pagination import PagedResultsSchema
from testspg.constants import FOM_DEV_APPLICATION_ID

APP_USER_ROLE_PAGED_RESULT_2_RECORDS = PagedResultsSchema[FamApplicationUserRoleAssignmentGetSchema](
  **{
    "meta": {
      "total": 2,
      "number_of_pages": 1,
      "page_number": 1,
      "page_size": 10
    },
    "results": [
      {
        "user_role_xref_id": 11,
        "user_id": 9,
        "role_id": 4,
        "user": {
          "user_name": "CMENG",
          "user_type": {
            "code": "I",
            "description": "IDIR"
          },
          "first_name": "Catherine",
          "last_name": "Meng",
          "email": "Catherine.Meng@gov.bc.ca"
        },
        "role": {
          "role_name": "FOM_REVIEWER",
          "role_type_code": "C",
          "application": {
            "application_id": 2,
            "application_name": "FOM_DEV",
            "application_description": "Forest Operations Map (DEV)"
          },
          "role_id": 4,
          "display_name": "Reviewer",
          "role_purpose": "Provides the privilege to review all FOMs in the system",
          "forest_client_relation": None,
          "parent_role": None
        },
        "create_date": "2024-11-01T19:44:47.497785Z"
      },
      {
        "user_role_xref_id": 12,
        "user_id": 10,
        "role_id": 128,
        "user": {
          "user_name": "OLIBERCH",
          "user_type": {
            "code": "I",
            "description": "IDIR"
          },
          "first_name": "Olga",
          "last_name": "Liberchuk",
          "email": "Olga.Liberchuk@gov.bc.ca"
        },
        "role": {
          "role_name": "FOM_SUBMITTER_00001011",
          "role_type_code": "C",
          "application": {
            "application_id": 2,
            "application_name": "FOM_DEV",
            "application_description": "Forest Operations Map (DEV)"
          },
          "role_id": 128,
          "display_name": "Submitter",
          "role_purpose": "Provides the privilege to submit a FOM (on behalf of a specific forest client) for 00001011",
          "forest_client_relation": {
            "client_name": None,
            "forest_client_number": "00001011",
            "status": None
          },
          "parent_role": {
            "role_name": "FOM_SUBMITTER",
            "role_type_code": "A",
            "application": {
              "application_id": 2,
              "application_name": "FOM_DEV",
              "application_description": "Forest Operations Map (DEV)"
            }
          },
        },
        "create_date": "2024-11-01T19:45:20.702148Z"
      }
    ]
  }
)

# sample end user permission granted response - role with no scope
sample_end_user_permission_granted_no_scope_details = FamUserRoleAssignmentCreateRes(
  **{'status_code': HTTPStatus.OK,
    'detail': FamApplicationUserRoleAssignmentGetSchema(
    user_role_xref_id=999, user_id=9, role_id=4,
    user=FamUserInfoSchema(user_name='enduser', first_name='first', last_name='last', email='a@b.com',
      user_type_relation=FamUserTypeSchema(user_type_code=UserType.BCEID, description='BCEID')),
    role=FamRoleWithClientSchema(role_name='FOM_REVIEWER', role_type_code='C',
    application=FamApplicationSchema(application_id=2, application_name='FOM_DEV', application_description='Forest Operations Map (DEV)'),
    role_id=999, display_name='Reviewer', role_purpose='Provides the privilege to review all FOMs in the system', forest_client_relation=None, parent_role=None),
    create_date=datetime(2024, 11, 1, 19, 44, 47),
    expiry_date=datetime(2025, 12, 31, 23, 59, 59, tzinfo=ZoneInfo("America/Vancouver"))),
    'error_message': None
  }
 )

# sample end user permission granted response - role with forest_client scope
sample_end_user_permission_granted_with_scope_details = FamUserRoleAssignmentCreateRes(
  **{'status_code': HTTPStatus.OK,
    'detail': FamApplicationUserRoleAssignmentGetSchema(
    user_role_xref_id=888, user_id=9, role_id=127,
    user=FamUserInfoSchema(user_name='enduser', first_name='first', last_name='last', email='a@b.com',
      user_type_relation=FamUserTypeSchema(user_type_code=UserType.BCEID, description='BCEID')),
    role=FamRoleWithClientSchema(role_name='FOM_SUBMITTER_00001012', role_type_code='C',
    application=FamApplicationSchema(application_id=2, application_name='FOM_DEV', application_description='Forest Operations Map (DEV)'),
    role_id=127, display_name='Submitter', role_purpose='Provides the privilege to submit a FOM (on behalf of a specific forest client)',
    forest_client_relation=FamForestClientSchema(client_name=None, forest_client_number="00001012", status=None),
    parent_role=FamRoleMinSchema(role_name="FOM_SUBMITTER", role_type_code="A",
      application=FamApplicationSchema(application_id=2, application_name='FOM_DEV', application_description='Forest Operations Map (DEV)'))),
    create_date=datetime(2024, 11, 1, 19, 44, 47),
    expiry_date=datetime(2025, 6, 30, 23, 59, 59, tzinfo=ZoneInfo("America/Vancouver"))),
    'error_message': None
  }
 )

sameple_user_role_with_no_client_revoked_record = FamUserRoleXref(**{
	"user_id": 111, "role_id": 999,
	"user": FamUser(**{"user_id": 111}),
	"role": FamRole(** {"display_name": "Reviewer", "application": FamApplication(** {"application_id": 2})})
})

sameple_user_role_with_client_revoked_record = FamUserRoleXref(**{
	"user_id": 111, "role_id": 999,
	"user": FamUser(**{"user_id": 111}),
	"role": FamRole(**{"display_name": "Submitter", "role_name": "FOM_SUBMITTER_00001011",
		"application": FamApplication(** {"application_id": FOM_DEV_APPLICATION_ID, }),
		"client_number_id": 3, "forest_client_relation": FamForestClient(**{
			"forest_client_number": "00001011"
		})
   })
})

sameple_user_role_with_notfound_client_revoked_record = FamUserRoleXref(**{
	"user_id": 111, "role_id": 999,
	"user": FamUser(**{"user_id": 111}),
	"role": FamRole(**{"display_name": "Submitter", "role_name": "FOM_SUBMITTER_09090909",
		"application": FamApplication(** {"application_id": FOM_DEV_APPLICATION_ID, }),
		"client_number_id": 3, "forest_client_relation": FamForestClient(**{
			"forest_client_number": "09090909"
		})
   })
})

# Helper function to create mock FamUserRoleAssignmentCreateRes for multi-user tests
def create_mock_user_role_assignment_success(
    user_role_xref_id: int,
    user_id: int,
    role_id: int,
    user_name: str,
    user_guid: str,
    user_type_code: UserType = UserType.IDIR,
    role_name: str = "FOM_SUBMITTER",
    application_id: int = FOM_DEV_APPLICATION_ID,
    expiry_date=None
) -> FamUserRoleAssignmentCreateRes:
    """
    Create a mock successful user role assignment response for testing.
    Matches the structure of sample_end_user_permission_granted_no_scope_details.
    """
    return FamUserRoleAssignmentCreateRes(
        status_code=HTTPStatus.OK,
        detail=FamApplicationUserRoleAssignmentGetSchema(
            user_role_xref_id=user_role_xref_id,
            user_id=user_id,
            role_id=role_id,
            user=FamUserInfoSchema(
                user_name=user_name,
                first_name='Test',
                last_name='User',
                email='test@example.com',
                user_type_relation=FamUserTypeSchema(
                    user_type_code=user_type_code,
                    description='IDIR' if user_type_code == UserType.IDIR else 'BCEID'
                )
            ),
            role=FamRoleWithClientSchema(
                role_name=role_name,
                role_type_code='C',
                application=FamApplicationSchema(
                    application_id=application_id,
                    application_name='FOM_DEV',
                    application_description='Forest Operations Map (DEV)'
                ),
                role_id=role_id,
                display_name='Submitter',
                role_purpose='Test role purpose',
                forest_client_relation=None,
                parent_role=None
            ),
            create_date=datetime(2024, 11, 1, 19, 44, 47),
            expiry_date=expiry_date
        ),
        error_message=None
    )


def create_mock_user_role_assignment_error(
    status_code: HTTPStatus,
    error_message: str,
    user_role_xref_id: int = None,
    user_id: int = None,
    role_id: int = None
) -> FamUserRoleAssignmentCreateRes:
    """
    Create a mock failed user role assignment response for testing.
    """
    return FamUserRoleAssignmentCreateRes(
        status_code=status_code,
        detail=None,
        error_message=error_message
    )