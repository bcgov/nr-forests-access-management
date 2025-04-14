
from api.app.schemas.schemas import FamAppAdminGetResponse

APP_ADMIN_MOCK_RESULT_4_JSON_RECORDS = [
    {
        "application_admin_id": 1,
        "user_id": 1,
        "application_id": 1,
        "user": {
            "user_name": "COGUSTAF",
            "user_type": {
            "code": "I",
            "description": "IDIR"
            },
            "first_name": None,
            "last_name": None,
            "email": None
        },
        "application": {
            "application_id": 1,
            "application_name": "FAM",
            "application_description": "Forests Access Management",
            "app_environment": None
        },
    },
    {
        "application_admin_id": 2,
        "user_id": 1,
        "application_id": 2,
        "user": {
            "user_name": "COGUSTAF",
            "user_type": {
            "code": "I",
            "description": "IDIR"
            },
            "first_name": None,
            "last_name": None,
            "email": None
        },
        "application": {
            "application_id": 2,
            "application_name": "FOM_DEV",
            "application_description": "Forest Operations Map (DEV)",
            "app_environment": "DEV"
        },
    },
    {
        "application_admin_id": 3,
        "user_id": 2,
        "application_id": 2,
        "user": {
            "user_name": "BVANDEGR",
            "user_type": {
            "code": "I",
            "description": "IDIR"
            },
            "first_name": None,
            "last_name": None,
            "email": None
        },
        "application": {
            "application_id": 2,
            "application_name": "FOM_DEV",
            "application_description": "Forest Operations Map (DEV)",
            "app_environment": "DEV"
        },
    },
    {
        "application_admin_id": 4,
        "user_id": 4,
        "application_id": 2,
        "user": {
            "user_name": "IANLIU",
            "user_type": {
            "code": "I",
            "description": "IDIR"
            },
            "first_name": None,
            "last_name": None,
            "email": None
        },
        "application": {
            "application_id": 2,
            "application_name": "FOM_DEV",
            "application_description": "Forest Operations Map (DEV)",
            "app_environment": "DEV"
        },
    }
]

APP_ADMIN_RESPONSE_SCHEMA_4_RECORDS = [
    FamAppAdminGetResponse(**record) for record in APP_ADMIN_MOCK_RESULT_4_JSON_RECORDS
]
