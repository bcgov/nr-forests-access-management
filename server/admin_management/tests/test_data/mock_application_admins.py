from api.app.schemas.schemas import FamAppAdminGetResponse
# Mock data for application admins for use in tests

MOCK_APPLICATION_ADMINS = [
    {
        "application_admin_id": 1,
        "application_id": 100,
        "user_id": 200,
        "created_by": "test_creator",
        "create_date": "2024-01-01T00:00:00Z",
        "updated_by": None,
        "updated_at": None,
        "user": {
            "user_id": 200,
            "user_name": "admin1",
            "user_type": {"code": "I", "description": "IDIR"}
        },
        "application": {
            "application_id": 100,
            "application_name": "TestApp",
            "application_description": "Test application"
        },
    },
    {
        "application_admin_id": 2,
        "application_id": 100,
        "user_id": 201,
        "created_by": "test_creator",
        "create_date": "2024-01-02T00:00:00Z",
        "updated_by": None,
        "updated_at": None,
        "user": {
            "user_id": 201,
            "user_name": "admin2",
            "user_type": {"code": "I", "description": "IDIR"}
        },
        "application": {
            "application_id": 100,
            "application_name": "TestApp",
            "application_description": "Test application"
        },
    },

]
