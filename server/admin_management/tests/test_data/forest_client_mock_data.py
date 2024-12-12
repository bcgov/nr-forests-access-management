
import datetime
from enum import Enum
from typing import List

from api.app.constants import AdminRoleAuthGroup, AppEnv, RoleType, UserType
from api.app.schemas.schemas import (AdminUserAccessResponse,
                                     FamAccessControlPrivilegeGetResponse,
                                     FamApplicationBase,
                                     FamApplicationGrantDto, FamAuthGrantDto,
                                     FamForestClientBase, FamGrantDetailDto,
                                     FamRoleBase, FamRoleGrantDto,
                                     FamRoleWithClientDto, FamUserInfoDto,
                                     FamUserTypeDto)

# --- mock data for test_forest_client_dec.py

class TestFcDecoratorFnResultConditions(str, Enum):
    NO_RESULT = "no_result"
    NO_FC_IN_RESULTS = "no_fc_results"
    WITH_FC_IN_RESULTS = "with_fc_results",
    WITH_FC_NOT_ACTIVE_RESULT = "with_fc_but_not_active_no_result"

"""
Mock data for `get_paged_delegated_admin_assignment_by_application_id()` return in PagedResultsSchema.results.
Use 'TestAccessControlResultDictKeys' enum to identify different set of data.
"""
APP_DELEGATED_ADMIN_ROLE_GET_RESULTS_NO_PAGE_META: dict[str, List[FamAccessControlPrivilegeGetResponse]] = {
    TestFcDecoratorFnResultConditions.NO_RESULT: [],
    TestFcDecoratorFnResultConditions.NO_FC_IN_RESULTS: [
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
    TestFcDecoratorFnResultConditions.WITH_FC_IN_RESULTS: [
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
    TestFcDecoratorFnResultConditions.WITH_FC_NOT_ACTIVE_RESULT: [
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

"""
Mock data for `AdminUserAccessService.get_access_grants()`.
Use 'TestAccessControlResultDictKeys' enum to identify different set of data.
"""
ADMIN_GET_ACCESS_PRIVILEGE_RESULTS: dict[str, AdminUserAccessResponse] = {
    TestFcDecoratorFnResultConditions.NO_RESULT: AdminUserAccessResponse(access=[]),
    TestFcDecoratorFnResultConditions.NO_FC_IN_RESULTS: AdminUserAccessResponse(
        access=[
            FamAuthGrantDto(auth_key=AdminRoleAuthGroup.FAM_ADMIN,
                grants=[
                    FamGrantDetailDto(application=FamApplicationGrantDto(application_id=1, application_name='FAM', description='Forests Access Management', env=None), roles=None),
                    FamGrantDetailDto(application=FamApplicationGrantDto(application_id=2, application_name='FOM', description='Forest Operations Map (DEV)', env=AppEnv.APP_ENV_TYPE_DEV), roles=None),
                    FamGrantDetailDto(application=FamApplicationGrantDto(application_id=3, application_name='FOM', description='Forest Operations Map (TEST)', env=AppEnv.APP_ENV_TYPE_TEST), roles=None),
                    FamGrantDetailDto(application=FamApplicationGrantDto(application_id=5, application_name='SPAR', description='Seed Planning and Registry Application (DEV)', env=AppEnv.APP_ENV_TYPE_DEV), roles=None),
                    FamGrantDetailDto(application=FamApplicationGrantDto(application_id=8, application_name='CLIENT', description='Forests Client Management System (DEV)', env=AppEnv.APP_ENV_TYPE_DEV), roles=None),
                ]
            ),
            FamAuthGrantDto(auth_key=AdminRoleAuthGroup.APP_ADMIN,
                grants=[
                    FamGrantDetailDto(
                        application=FamApplicationGrantDto(application_id=2, application_name='FOM', description='Forest Operations Map (DEV)', env=AppEnv.APP_ENV_TYPE_DEV),
                        roles=[
                            FamRoleGrantDto(role_id=3, role_name='FOM_SUBMITTER', display_name='Submitter', role_purpose='Provides the privilege to submit a FOM (on behalf of a specific forest client)', role_type_code=RoleType.ROLE_TYPE_ABSTRACT, forest_clients=None),
                            FamRoleGrantDto(role_id=4, role_name='FOM_REVIEWER', display_name='Reviewer', role_purpose='Provides the privilege to review all FOMs in the system', role_type_code=RoleType.ROLE_TYPE_CONCRETE, forest_clients=None)
                        ]
                    )
                ]
            )
        ]
    ),
    TestFcDecoratorFnResultConditions.WITH_FC_IN_RESULTS: AdminUserAccessResponse(
        access=[
            FamAuthGrantDto(auth_key=AdminRoleAuthGroup.APP_ADMIN,
                grants=[
                    FamGrantDetailDto(
                        application=FamApplicationGrantDto(application_id=2, application_name='FOM', description='Forest Operations Map (DEV)', env=AppEnv.APP_ENV_TYPE_DEV),
                        roles=[
                            FamRoleGrantDto(role_id=3, role_name='FOM_SUBMITTER', display_name='Submitter', role_purpose='Provides the privilege to submit a FOM (on behalf of a specific forest client)', role_type_code=RoleType.ROLE_TYPE_ABSTRACT, forest_clients=None),
                            FamRoleGrantDto(role_id=4, role_name='FOM_REVIEWER', display_name='Reviewer', role_purpose='Provides the privilege to review all FOMs in the system', role_type_code=RoleType.ROLE_TYPE_CONCRETE, forest_clients=None)
                        ]
                    )
                ]
            ),
            FamAuthGrantDto(auth_key=AdminRoleAuthGroup.DELEGATED_ADMIN,
                grants=[
                    FamGrantDetailDto(
                        application=FamApplicationGrantDto(application_id=2, application_name='FOM', description='Forest Operations Map (DEV)', env=AppEnv.APP_ENV_TYPE_DEV),
                        roles=[
                            FamRoleGrantDto(role_id=3, role_name='FOM_SUBMITTER', display_name='Submitter', role_purpose='Provides the privilege to submit a FOM (on behalf of a specific forest client)', role_type_code=RoleType.ROLE_TYPE_ABSTRACT,
                                            forest_clients=[
                                FamForestClientBase(forest_client_number='00001011'),
                                FamForestClientBase(forest_client_number='00001012')
                            ]),
                            FamRoleGrantDto(role_id=4, role_name='FOM_REVIEWER', display_name='Reviewer', role_purpose='Provides the privilege to review all FOMs in the system', role_type_code=RoleType.ROLE_TYPE_CONCRETE, forest_clients=None)
                        ]
                    ),
                    FamGrantDetailDto(
                        application=FamApplicationGrantDto(application_id=5, application_name='SPAR', description='Seed Planning and Registry Application (DEV)', env=AppEnv.APP_ENV_TYPE_DEV),
                        roles=[
                            FamRoleGrantDto(role_id=149, role_name='SPAR_NONMINISTRY_ORCHARD', display_name='Submitter (Non-Ministry)', role_purpose='Allow non ministry users to create, review, update and submit A class registration forms. Non-Ministry users may enter and update lots where their sign in client profile matches the Applicant Client', role_type_code=RoleType.ROLE_TYPE_ABSTRACT,
                                            forest_clients=[
                                FamForestClientBase(forest_client_number='00012797')
                            ]),
                        ]
                    )
                ]
            )
        ]
    ),
    TestFcDecoratorFnResultConditions.WITH_FC_NOT_ACTIVE_RESULT: AdminUserAccessResponse(
        access=[
            FamAuthGrantDto(auth_key=AdminRoleAuthGroup.DELEGATED_ADMIN,
                grants=[
                    FamGrantDetailDto(
                        application=FamApplicationGrantDto(application_id=900, application_name='dummy_app', env=AppEnv.APP_ENV_TYPE_DEV),
                        roles=[
                            FamRoleGrantDto(role_id=990, role_name='r1', display_name='Test dummy role', role_type_code=RoleType.ROLE_TYPE_ABSTRACT, role_purpose="Test dummy role",
                                            forest_clients=[
                                FamForestClientBase(forest_client_number='12345678'),
                                FamForestClientBase(forest_client_number='99999999')
                            ])
                        ]
                    )
                ]
            )
        ]
    )
}