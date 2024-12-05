
import datetime
from enum import Enum
from typing import List

from api.app.constants import RoleType, UserType
from api.app.schemas.fam_application import FamApplicationSchema
from api.app.schemas.fam_application_user_role_assignment_get import \
    FamApplicationUserRoleAssignmentGetSchema
from api.app.schemas.fam_forest_client import FamForestClientSchema
from api.app.schemas.fam_role_min import FamRoleMinSchema
from api.app.schemas.fam_role_with_client import FamRoleWithClientSchema
from api.app.schemas.fam_user_info import FamUserInfoSchema
from api.app.schemas.fam_user_type import FamUserTypeSchema

# --- mock data for test_forest_client_dec.py

class TestAppUserRoleResultDictKeys(str, Enum):
    NO_RESULT = "no_result"
    NO_FC_RESULTS = "no_fc_results"
    WITH_FC_RESULTS = "with_fc_results"

"""
Mock data for `get_application_role_assignments()` return in PagedResultsSchema.results.
Use 'TestAppUserRoleResultDictKeys' enum to identify different set of data.
"""
APP_USER_ROLE_GET_RESULTS_NO_PAGE_META: dict[str, List[FamApplicationUserRoleAssignmentGetSchema]] = {
    TestAppUserRoleResultDictKeys.NO_RESULT: [],
    TestAppUserRoleResultDictKeys.NO_FC_RESULTS: [
        FamApplicationUserRoleAssignmentGetSchema(user_role_xref_id=900, user_id=900, role_id=900,
            user=FamUserInfoSchema(user_name="tu_1", user_type_relation=FamUserTypeSchema(user_type_code=UserType.BCEID, description="dummy_desc")),
            role=FamRoleWithClientSchema(role_id=900, role_name="r1", role_type_code=RoleType.ROLE_TYPE_CONCRETE, role_purpose="Test dummy role",
                application=FamApplicationSchema(
                    application_id=900, application_name="a1", application_description="dummy_app"
                ),
                forest_client_relation=None),
            create_date=datetime.datetime(2024, 11, 1, 19, 44, 47)),
        FamApplicationUserRoleAssignmentGetSchema(user_role_xref_id=901, user_id=901, role_id=901,
            user=FamUserInfoSchema(user_name="tu_2", user_type_relation=FamUserTypeSchema(user_type_code=UserType.BCEID, description="dummy_desc")),
            role=FamRoleWithClientSchema(role_id=901, role_name="r1", role_type_code=RoleType.ROLE_TYPE_CONCRETE, role_purpose="Test dummy role",
                application=FamApplicationSchema(
                    application_id=901, application_name="a1", application_description="dummy_app"
                ),
                forest_client_relation=None
            ),
            create_date=datetime.datetime(2024, 11, 1, 19, 44, 47)),
    ],
    TestAppUserRoleResultDictKeys.WITH_FC_RESULTS: [
        FamApplicationUserRoleAssignmentGetSchema(user_role_xref_id=902, user_id=903, role_id=990,
            user=FamUserInfoSchema(user_name="tu_1", user_type_relation=FamUserTypeSchema(user_type_code=UserType.BCEID, description="dummy_desc")),
            role=FamRoleWithClientSchema(role_id=990, role_name="r2_00001011", role_type_code=RoleType.ROLE_TYPE_CONCRETE, role_purpose="Test dummy role",
                application=FamApplicationSchema(
                    application_id=990, application_name="a1", application_description="dummy_app"
                ), forest_client_relation=FamForestClientSchema(forest_client_number="00001011"), parent_role=FamRoleMinSchema(role_name="r2",
                role_type_code=RoleType.ROLE_TYPE_ABSTRACT, application=FamApplicationSchema(application_id=900, application_name="a1",
                application_description="dummy_app")
            )),
            create_date=datetime.datetime(2024, 11, 1, 19, 44, 47)), # FC
        FamApplicationUserRoleAssignmentGetSchema(user_role_xref_id=903, user_id=904, role_id=991,
            user=FamUserInfoSchema(user_name="tu_1", user_type_relation=FamUserTypeSchema(user_type_code=UserType.BCEID, description="dummy_desc")),
            role=FamRoleWithClientSchema(role_id=991, role_name="r2_00001012", role_type_code=RoleType.ROLE_TYPE_CONCRETE, role_purpose="Test dummy role",
                application=FamApplicationSchema(
                    application_id=900, application_name="a1", application_description="dummy_app"
                ), forest_client_relation=FamForestClientSchema(forest_client_number="00001012"), parent_role=FamRoleMinSchema(role_name="r2",
                role_type_code=RoleType.ROLE_TYPE_ABSTRACT, application=FamApplicationSchema(application_id=900, application_name="a1",
                application_description="dummy_app")
            )),
            create_date=datetime.datetime(2024, 11, 1, 19, 44, 47)), # FC
        FamApplicationUserRoleAssignmentGetSchema(user_role_xref_id=900, user_id=900, role_id=900,
            user=FamUserInfoSchema(user_name="tu_1", user_type_relation=FamUserTypeSchema(user_type_code=UserType.BCEID, description="dummy_desc")),
            role=FamRoleWithClientSchema(role_id=900, role_name="r1", role_type_code=RoleType.ROLE_TYPE_CONCRETE, role_purpose="Test dummy role",
                application=FamApplicationSchema(
                    application_id=900, application_name="a1", application_description="dummy_app"
                ),
                forest_client_relation=None
            ),
            create_date=datetime.datetime(2024, 11, 1, 19, 44, 47)) # no FC
    ]
}
