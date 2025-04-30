
from datetime import datetime
from http import HTTPStatus

from api.app.constants import UserType
from api.app.models.model import (FamAccessControlPrivilege, FamApplication,
                                  FamForestClient, FamRole, FamUser)
from api.app.schemas.pagination import PagedResultsSchema
from api.app.schemas.schemas import (FamAccessControlPrivilegeCreateResponse,
                                     FamAccessControlPrivilegeGetResponse,
                                     FamApplicationBase, FamForestClientBase,
                                     FamRoleBase, FamRoleWithClientDto,
                                     FamUserInfoDto, FamUserTypeDto)
from tests.constants import TEST_APPLICATION_ID_FOM_DEV

APP_DELEGATED_ADMIN_MOCK_RESULT_4_JSON_RECORDS = [
{
    "access_control_privilege_id": 3,
    "user_id": 5,
    "role_id": 127,
    "user": {
        "user_name": "PTOLLEST",
        "user_type": {
        "code": "I",
        "description": "IDIR"
        },
        "first_name": None,
        "last_name": None,
        "email": None
    },
    "role": {
        "role_id": 127,
        "role_name": "FOM_SUBMITTER_00001018",
        "display_name": "Submitter",
        "role_purpose": "Provides the privilege to submit a FOM (on behalf of a specific forest client) for 00001018",
        "forest_client_relation": {
        "client_name": "SNEATH",
        "forest_client_number": "00001018"
        },
        "parent_role": {
        "role_name": "FOM_SUBMITTER",
        "role_type_code": "A"
        },
        "application": {
        "application_id": 2,
        "application_name": "FOM_DEV",
        "application_description": "Forest Operations Map (DEV)",
        "app_environment": "DEV"
        }
    },
    "create_date": "2024-12-13T00:00:00"
    },
    {
    "access_control_privilege_id": 1,
    "user_id": 5,
    "role_id": 4,
    "user": {
        "user_name": "PTOLLEST",
        "user_type": {
        "code": "I",
        "description": "IDIR"
        },
        "first_name": None,
        "last_name": None,
        "email": None
    },
    "role": {
        "role_id": 4,
        "role_name": "FOM_REVIEWER",
        "display_name": "Reviewer",
        "role_purpose": "Provides the privilege to review all FOMs in the system",
        "forest_client_relation": None,
        "parent_role": None,
        "application": {
        "application_id": 2,
        "application_name": "FOM_DEV",
        "application_description": "Forest Operations Map (DEV)",
        "app_environment": "DEV"
        }
    },
    "create_date": "2024-12-13T00:00:00"
    },
    {
    "access_control_privilege_id": 4,
    "user_id": 6,
    "role_id": 127,
    "user": {
        "user_name": "TEST-3-LOAD-CHILD-1",
        "user_type": {
        "code": "B",
        "description": "Business BCeID"
        },
        "first_name": None,
        "last_name": None,
        "email": None
    },
    "role": {
        "role_id": 127,
        "role_name": "FOM_SUBMITTER_00001018",
        "display_name": "Submitter",
        "role_purpose": "Provides the privilege to submit a FOM (on behalf of a specific forest client) for 00001018",
        "forest_client_relation": {
        "client_name": "SNEATH",
        "forest_client_number": "00001018"
        },
        "parent_role": {
        "role_name": "FOM_SUBMITTER",
        "role_type_code": "A"
        },
        "application": {
        "application_id": 2,
        "application_name": "FOM_DEV",
        "application_description": "Forest Operations Map (DEV)",
        "app_environment": "DEV"
        }
    },
    "create_date": "2024-12-13T00:00:00"
    },
    {
    "access_control_privilege_id": 2,
    "user_id": 6,
    "role_id": 4,
    "user": {
        "user_name": "TEST-3-LOAD-CHILD-1",
        "user_type": {
        "code": "B",
        "description": "Business BCeID"
        },
        "first_name": None,
        "last_name": None,
        "email": None
    },
    "role": {
        "role_id": 4,
        "role_name": "FOM_REVIEWER",
        "display_name": "Reviewer",
        "role_purpose": "Provides the privilege to review all FOMs in the system",
        "forest_client_relation": None,
        "parent_role": None,
        "application": {
        "application_id": 2,
        "application_name": "FOM_DEV",
        "application_description": "Forest Operations Map (DEV)",
        "app_environment": "DEV"
        }
    },
    "create_date": "2024-12-13T00:00:00"
    }
]

APP_DELEGATED_ADMIN_RESPONSE_SCHEMA_4_RECORDS = [
    FamAccessControlPrivilegeGetResponse(**record) for record in APP_DELEGATED_ADMIN_MOCK_RESULT_4_JSON_RECORDS
]

APP_DELEGATED_ADMIN_PAGED_RESULT_4_RECORDS = PagedResultsSchema[FamAccessControlPrivilegeGetResponse](
    **{
    "meta": {
        "total": 4,
        "number_of_pages": 1,
        "page_number": 1,
        "page_size": 50
    },
    "results": APP_DELEGATED_ADMIN_MOCK_RESULT_4_JSON_RECORDS
})

# sample end user permission granted response - role with no scope
sample_delegated_admin_permission_granted_no_scope_details = FamAccessControlPrivilegeCreateResponse(
	**{'status_code': HTTPStatus.OK,
		'detail': FamAccessControlPrivilegeGetResponse(
		access_control_privilege_id=999, user_id=9, role_id=4,
		user=FamUserInfoDto(user_name='dadminuser', first_name='first', last_name='last', email='a@b.com',
			user_type_relation=FamUserTypeDto(user_type_code=UserType.BCEID, description='BCEID')),
		role=FamRoleWithClientDto(role_name='FOM_REVIEWER',
		application=FamApplicationBase(application_id=2, application_name='FOM_DEV', application_description='Forest Operations Map (DEV)'),
		role_id=999, display_name='Reviewer', role_purpose='Provides the privilege to review all FOMs in the system', forest_client_relation=None, parent_role=None),
		create_date=datetime(2024, 11, 1, 19, 44, 47)),
		'error_message': None
	}
 )

# sample delegated admin permission granted response - role with forest_client scope
sample_delegated_admin_permission_granted_with_scope_details = FamAccessControlPrivilegeCreateResponse(
	**{'status_code': HTTPStatus.OK,
		'detail': FamAccessControlPrivilegeGetResponse(
		access_control_privilege_id=888, user_id=9, role_id=127,
		user=FamUserInfoDto(user_name='dadminuser', first_name='first', last_name='last', email='a@b.com',
			user_type_relation=FamUserTypeDto(user_type_code=UserType.BCEID, description='BCEID')),
		role=FamRoleWithClientDto(role_name='FOM_SUBMITTER_00001012',
		application=FamApplicationBase(application_id=2, application_name='FOM_DEV', application_description='Forest Operations Map (DEV)'),
		role_id=127, display_name='Submitter', role_purpose='Provides the privilege to submit a FOM (on behalf of a specific forest client)',
		forest_client_relation=FamForestClientBase(client_name=None, forest_client_number="00001012", status=None),
		parent_role=FamRoleBase(role_name="FOM_SUBMITTER", role_type_code="A",
			application=FamApplicationBase(application_id=2, application_name='FOM_DEV', application_description='Forest Operations Map (DEV)'))),
			create_date=datetime(2024, 11, 1, 19, 44, 47)),
		'error_message': None
	}
 )

sameple_delegated_admin_role_with_no_client_revoked_record = FamAccessControlPrivilege(**{
	"user_id": 111, "role_id": 999,
	"user": FamUser(**{"user_id": 111}),
	"role": FamRole(** {"display_name": "Reviewer",
		"application": FamApplication(** {"application_id": TEST_APPLICATION_ID_FOM_DEV})
	})
})

sameple_delegated_admin_role_with_client_revoked_record = FamAccessControlPrivilege(**{
	"user_id": 111, "role_id": 999,
	"user": FamUser(**{"user_id": 111}),
	"role": FamRole(**{"display_name": "Submitter", "role_name": "FOM_SUBMITTER_00001011",
		"application": FamApplication(** {"application_id": TEST_APPLICATION_ID_FOM_DEV, }),
		"client_number_id": 3, "forest_client_relation": FamForestClient(**{
			"forest_client_number": "00001011"
		})
   })
})

sameple_delegated_admin_role_with_notfound_client_revoked_record = FamAccessControlPrivilege(**{
	"user_id": 111, "role_id": 999,
	"user": FamUser(**{"user_id": 111}),
	"role": FamRole(**{"display_name": "Submitter", "role_name": "FOM_SUBMITTER_09090909",
		"application": FamApplication(** {"application_id": TEST_APPLICATION_ID_FOM_DEV, }),
		"client_number_id": 3, "forest_client_relation": FamForestClient(**{
			"forest_client_number": "09090909"
		})
   })
})