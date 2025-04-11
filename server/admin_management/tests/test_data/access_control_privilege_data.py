
from typing import List

from api.app.schemas.pagination import PagedResultsSchema
from api.app.schemas.schemas import FamAccessControlPrivilegeGetResponse

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