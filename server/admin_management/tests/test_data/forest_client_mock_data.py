
import datetime
from enum import Enum
from typing import List

from api.app.constants import AppEnv, RoleType, UserType
from api.app.schemas.schemas import (FamAccessControlPrivilegeGetResponse,
                                     FamApplicationBase, FamForestClientBase,
                                     FamRoleBase, FamRoleWithClientDto,
                                     FamUserInfoDto, FamUserTypeDto)

# --- mock data for test_forest_client_dec.py

class TestAccessControlResultDictKeys(str, Enum):
    NO_RESULT = "no_result"
    NO_FC_IN_RESULTS = "no_fc_results"
    WITH_FC_IN_RESULTS = "with_fc_results",
    WITH_FC_NOT_ACTIVE_RESULT = "with_fc_but_not_active_no_result"

"""
Mock data for `get_paged_delegated_admin_assignment_by_application_id()` return in PagedResultsSchema.results.
Use 'TestAccessControlResultDictKeys' enum to identify different set of data.
"""
APP_DELEGATED_ADMIN_ROLE_GET_RESULTS_NO_PAGE_META: dict[str, List[FamAccessControlPrivilegeGetResponse]] = {
    TestAccessControlResultDictKeys.NO_RESULT: [],
    TestAccessControlResultDictKeys.NO_FC_IN_RESULTS: [
        FamAccessControlPrivilegeGetResponse(access_control_privilege_id=900, user_id=900, role_id=900,
            user=FamUserInfoDto(user_name="tu_1", user_type_relation=FamUserTypeDto(user_type_code=UserType.BCEID, description="dummy_desc")),
            role=FamRoleWithClientDto(role_id=900, role_name="r1", role_type_code=RoleType.ROLE_TYPE_CONCRETE, role_purpose="Test dummy role",
                application=FamApplicationBase(
                    application_id=900, application_name="a1", application_description="dummy_app", app_environment=AppEnv.APP_ENV_TYPE_DEV
                ),
                forest_client_relation=None),
            create_date=datetime.datetime(2024, 11, 1, 19, 44, 47)),
        FamAccessControlPrivilegeGetResponse(access_control_privilege_id=901, user_id=901, role_id=901,
            user=FamUserInfoDto(user_name="tu_2", user_type_relation=FamUserTypeDto(user_type_code=UserType.BCEID, description="dummy_desc")),
            role=FamRoleWithClientDto(role_id=901, role_name="r1", role_type_code=RoleType.ROLE_TYPE_CONCRETE, role_purpose="Test dummy role",
                application=FamApplicationBase(
                    application_id=901, application_name="a1", application_description="dummy_app", app_environment=AppEnv.APP_ENV_TYPE_DEV
                ),
                forest_client_relation=None
            ),
            create_date=datetime.datetime(2024, 11, 1, 19, 44, 47)),
    ],
    TestAccessControlResultDictKeys.WITH_FC_IN_RESULTS: [
        FamAccessControlPrivilegeGetResponse(access_control_privilege_id=902, user_id=903, role_id=990,
            user=FamUserInfoDto(user_name="tu_1", user_type_relation=FamUserTypeDto(user_type_code=UserType.BCEID, description="dummy_desc")),
            role=FamRoleWithClientDto(role_id=990, role_name="r2_00001011", role_type_code=RoleType.ROLE_TYPE_CONCRETE, role_purpose="Test dummy role",
                application=FamApplicationBase(
                    application_id=990, application_name="a1", application_description="dummy_app", app_environment=AppEnv.APP_ENV_TYPE_DEV
                ), forest_client_relation=FamForestClientBase(forest_client_number="00001011"), parent_role=FamRoleBase(role_name="r2",
                role_type_code=RoleType.ROLE_TYPE_ABSTRACT, application=FamApplicationBase(application_id=900, application_name="a1",
                application_description="dummy_app")
            )),
            create_date=datetime.datetime(2024, 11, 1, 19, 44, 47)), # FC
        FamAccessControlPrivilegeGetResponse(access_control_privilege_id=903, user_id=904, role_id=991,
            user=FamUserInfoDto(user_name="tu_1", user_type_relation=FamUserTypeDto(user_type_code=UserType.BCEID, description="dummy_desc")),
            role=FamRoleWithClientDto(role_id=991, role_name="r2_00001012", role_type_code=RoleType.ROLE_TYPE_CONCRETE, role_purpose="Test dummy role",
                application=FamApplicationBase(
                    application_id=900, application_name="a1", application_description="dummy_app", app_environment=AppEnv.APP_ENV_TYPE_DEV
                ), forest_client_relation=FamForestClientBase(forest_client_number="00001012"), parent_role=FamRoleBase(role_name="r2",
                role_type_code=RoleType.ROLE_TYPE_ABSTRACT, application=FamApplicationBase(application_id=900, application_name="a1",
                application_description="dummy_app")
            )),
            create_date=datetime.datetime(2024, 11, 1, 19, 44, 47)), # FC
        FamAccessControlPrivilegeGetResponse(access_control_privilege_id=900, user_id=900, role_id=900,
            user=FamUserInfoDto(user_name="tu_1", user_type_relation=FamUserTypeDto(user_type_code=UserType.BCEID, description="dummy_desc")),
            role=FamRoleWithClientDto(role_id=900, role_name="r1", role_type_code=RoleType.ROLE_TYPE_CONCRETE, role_purpose="Test dummy role",
                application=FamApplicationBase(
                    application_id=900, application_name="a1", application_description="dummy_app", app_environment=AppEnv.APP_ENV_TYPE_DEV
                ),
                forest_client_relation=None
            ),
            create_date=datetime.datetime(2024, 11, 1, 19, 44, 47)) # no FC
    ],
    TestAccessControlResultDictKeys.WITH_FC_NOT_ACTIVE_RESULT: [
       FamAccessControlPrivilegeGetResponse(access_control_privilege_id=904, user_id=904, role_id=992,
            user=FamUserInfoDto(user_name="tu_1", user_type_relation=FamUserTypeDto(user_type_code=UserType.BCEID, description="dummy_desc")),
            role=FamRoleWithClientDto(role_id=992, role_name="r2_12345678", role_type_code=RoleType.ROLE_TYPE_CONCRETE, role_purpose="Test dummy role",
                application=FamApplicationBase(
                    application_id=900, application_name="a1", application_description="dummy_app", app_environment=AppEnv.APP_ENV_TYPE_DEV
                ), forest_client_relation=FamForestClientBase(forest_client_number="12345678"), parent_role=FamRoleBase(role_name="r2",
                role_type_code=RoleType.ROLE_TYPE_ABSTRACT, application=FamApplicationBase(application_id=900, application_name="a1",
                application_description="dummy_app")
            )),
            create_date=datetime.datetime(2024, 11, 1, 19, 44, 47)), # FC exist in db but not valid (legacy data or not active)
    ]
}
