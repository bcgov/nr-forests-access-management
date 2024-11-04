
from api.app.schemas.fam_application_user_role_assignment_get import \
    FamApplicationUserRoleAssignmentGetSchema
from api.app.schemas.pagination import PagedResultsSchema

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
          "client_number": None,
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
          "client_number": {
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