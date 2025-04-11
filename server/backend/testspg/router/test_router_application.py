import logging
from http import HTTPStatus
from unittest.mock import Mock

import pytest
import starlette.testclient
import testspg.jwt_utils as jwt_utils
from api.app.constants import (CURRENT_TERMS_AND_CONDITIONS_VERSION,
                               DEFAULT_PAGE_SIZE,
                               ERROR_CODE_INVALID_APPLICATION_ID,
                               ERROR_CODE_TERMS_CONDITIONS_REQUIRED, MIN_PAGE,
                               SortOrderEnum, UserRoleSortByEnum, UserType)
from api.app.crud import crud_application
from api.app.main import apiPrefix
from api.app.models.model import FamUserTermsConditions
from api.app.routers.router_application import router
from api.app.routers.router_guards import (
    authorize_by_app_id, enforce_bceid_terms_conditions_guard)
from api.app.schemas.pagination import UserRolePageParamsSchema
from sqlalchemy import insert
from testspg.constants import (ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID,
                               ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID_L3T,
                               ACCESS_GRANT_FOM_DEV_AR_00000001_IDIR,
                               ACCESS_GRANT_FOM_DEV_AR_00001018_BCEID_L3T,
                               ACCESS_GRANT_FOM_DEV_AR_00001018_BCEID_L4T,
                               ACCESS_GRANT_FOM_DEV_AR_00001018_IDIR,
                               ACCESS_GRANT_FOM_DEV_CR_BCEID_L3T,
                               ACCESS_GRANT_FOM_DEV_CR_BCEID_L4T,
                               ACCESS_GRANT_FOM_DEV_CR_IDIR,
                               FOM_DEV_APPLICATION_ID, NOT_EXIST_ROLE_NAME,
                               NOT_EXIST_TEST_USER_ID, ROLE_NAME_FOM_REVIEWER,
                               ROLE_NAME_FOM_SUBMITTER_00000001,
                               ROLE_NAME_FOM_SUBMITTER_00001018, TEST_CREATOR,
                               TEST_USER_ID, USER_NAME_BCEID_LOAD_3_TEST)
from testspg.test_data.app_user_roles_mock_data import \
    APP_USER_ROLE_PAGED_RESULT_2_RECORDS

LOGGER = logging.getLogger(__name__)
end_point = f"{apiPrefix}/fam-applications"
end_point_user_by_id = f"{end_point}/{{application_id}}/users/{{user_id}}"

# GET enpoint for users' access grants.
# ("{apiPrefix}/fam-applications/{application_id}/user-role-assignment")
get_application_role_assignment_end_point = (
    end_point + f"/{FOM_DEV_APPLICATION_ID}/user-role-assignment"
)

TEST_APPLICATION_NAME_FOM_DEV = "FOM_DEV"
TEST_APPLICATION_ROLES_FOM_DEV = ["FOM_SUBMITTER", "FOM_REVIEWER"]
TEST_APPLICATION_ID_NOT_FOUND = 0
ACCESS_ROLES_FOM_DEV_ONLY = ["FOM_DEV_ADMIN"]


@pytest.fixture(scope="function")
def get_fam_application_user_role_assignment_dependencies_override(test_client_fixture):
    """
    Helper fixture for unit testing to override dependencies
    for endpoint 'get_fam_application_user_role_assignment'
    """
    app = test_client_fixture.app
    app.dependency_overrides[authorize_by_app_id] = lambda: None
    app.dependency_overrides[enforce_bceid_terms_conditions_guard] = lambda: None
    yield test_client_fixture


def test_get_fam_application_user_role_assignment_no_matching_application(
    test_client_fixture: starlette.testclient.TestClient, test_rsa_key
):
    role_assignment_end_point = (
        end_point + f"/{TEST_APPLICATION_ID_NOT_FOUND}/user-role-assignment"
    )
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        role_assignment_end_point, headers=jwt_utils.headers(token)
    )
    data = response.json()
    assert data["detail"]["code"] == ERROR_CODE_INVALID_APPLICATION_ID


def test_get_fam_application_user_role_assignment_no_role_assignments(
    test_client_fixture: starlette.testclient.TestClient, test_rsa_key
):
    # test no user role assignment for the application
    token = jwt_utils.create_jwt_token(test_rsa_key, ACCESS_ROLES_FOM_DEV_ONLY)
    response = test_client_fixture.get(
        get_application_role_assignment_end_point, headers=jwt_utils.headers(token)
    )
    data = response.json().get("results")
    assert len(data) == 0  # initially no one is assigned with FOM_DEV roles


def test_get_fam_application_user_role_assignment_concrete_role(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    override_depends__get_verified_target_user,
):
    # override router guard dependencies
    override_depends__get_verified_target_user()

    # test user role assignment
    # create
    token = jwt_utils.create_jwt_token(test_rsa_key, ACCESS_ROLES_FOM_DEV_ONLY)
    response = test_client_fixture.post(
        f"{apiPrefix}/user-role-assignment",
        json=ACCESS_GRANT_FOM_DEV_CR_IDIR,
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == 200
    concrete_role_data = response.json().get("assignments_detail")[0]["detail"]

    # check
    response = test_client_fixture.get(
        get_application_role_assignment_end_point, headers=jwt_utils.headers(token)
    )
    data = response.json().get("results")
    assert len(data) == 1
    assert data[0]["user_role_xref_id"] == concrete_role_data["user_role_xref_id"]
    assert (
        data[0]["user"]["user_type"]["code"]
        == ACCESS_GRANT_FOM_DEV_CR_IDIR["user_type_code"]
    )
    assert data[0]["user"]["user_name"] == ACCESS_GRANT_FOM_DEV_CR_IDIR["user_name"]
    assert data[0]["role"]["role_type_code"] == "C"
    assert data[0]["role"]["role_name"] == "FOM_REVIEWER"


def test_get_fam_application_user_role_assignment_abstract_role(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    override_depends__get_verified_target_user,
):
    # override router guard dependencies
    override_depends__get_verified_target_user(ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID)

    # test user role assignment for abstract role
    # create
    token = jwt_utils.create_jwt_token(test_rsa_key, ACCESS_ROLES_FOM_DEV_ONLY)
    response = test_client_fixture.post(
        f"{apiPrefix}/user-role-assignment",
        json=ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID,
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == 200
    abstract_role_data = response.json().get("assignments_detail")[0]["detail"]

    # check
    response = test_client_fixture.get(
        get_application_role_assignment_end_point, headers=jwt_utils.headers(token)
    )
    data = response.json().get("results")
    assert len(data) == 1
    assert data[0]["user_role_xref_id"] == abstract_role_data["user_role_xref_id"]
    assert (
        data[0]["user"]["user_type"]["code"]
        == ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID["user_type_code"]
    )
    assert (
        data[0]["user"]["user_name"]
        == ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID["user_name"]
    )
    assert data[0]["role"]["role_type_code"] == "C"
    assert (
        data[0]["role"]["role_name"]
        == "FOM_SUBMITTER"
        + "_"
        + ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID["forest_client_numbers"][0]
    )
    assert data[0]["role"]["parent_role"]["role_type_code"] == "A"
    assert data[0]["role"]["parent_role"]["role_name"] == "FOM_SUBMITTER"


def test_fam_application_endpoints_invlid_path_application_id_type(
    test_client_fixture: starlette.testclient.TestClient, test_rsa_key
):
    token = jwt_utils.create_jwt_token(test_rsa_key)
    # endpoint path /{application_id} should be int type, provided as invalid str type.
    invalid_path_param = "not-int-str-application-id"
    invalid_path_router_msg = "Input should be a valid integer"

    # endpont GET: /{application_id}/user-role-assignment
    application_role_assignment_endpoint = (
        end_point + f"/{invalid_path_param}/user-role-assignment"
    )
    response = test_client_fixture.get(
        application_role_assignment_endpoint, headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert invalid_path_router_msg in response.text


# ---------------- Test get application user role assignment filtering scenarios ------------ #


def test_get_user_role_assignments_filtering_for_app_admin(
    test_client_fixture,
    create_test_user_role_assignments,
    fom_dev_access_admin_token,
):
    """
    The test focus on filtering of the GET endpoint for application's user/role
    return (get_fam_application_user_role_assignment) for APP_ADMIN role.

    The test uses application "FOM_DEV" and verifies login user who has
    FOM_DEV_ADMIN (application admin) should be able to see every user/role
    for this specific application.
    """
    # --- Prepare

    # Setup various user grants for different user_type(s), role_type(s),
    #   forest_client role scope and organizations.
    # Use these setup to verify visibility for the user (APP_ADMIN).
    access_grants = [
        ACCESS_GRANT_FOM_DEV_CR_IDIR,  # IDIR FOM_REVIEWER
        ACCESS_GRANT_FOM_DEV_CR_BCEID_L3T,  # BCEID FOM_REVIEWER L3T (org 1)
        ACCESS_GRANT_FOM_DEV_CR_BCEID_L4T,  # BCEID FOM_REVIEWER L4T (org 2)
        ACCESS_GRANT_FOM_DEV_AR_00001018_BCEID_L3T,  # BCEID FOM_SUBMITTER FC1 L3T (org 1)
        ACCESS_GRANT_FOM_DEV_AR_00001018_BCEID_L4T,  # BCEID FOM_SUBMITTER FC1 L4T (org 2)
        ACCESS_GRANT_FOM_DEV_AR_00000001_IDIR,  # IDIR FOM_SUBMITTER FC2
    ]

    # --- Create users' access grants for FOM_DEV application.
    access_grants_created = create_test_user_role_assignments(
        fom_dev_access_admin_token, access_grants
    )

    # Call GET endpoint with FOM_DEV_ADMIN application admin user level to
    # obtain access grants for FOM_DEV application.
    token = fom_dev_access_admin_token
    access_grants_response = test_client_fixture.get(
        get_application_role_assignment_end_point, headers=jwt_utils.headers(token)
    )
    response_data = access_grants_response.json().get("results")

    # --- Verify
    # APP_ADMIN should have visibility for FOM_DEV all user access grants.

    # verify access grants created result length is the same as
    #   access grants requested.
    assert len(access_grants) == len(access_grants_created)

    # verify FOM_DEV_ADMIN GET result contains exact set of user_role_xref_id
    #   created from assigned user role assignments.
    assert len(response_data) == len(access_grants_created)
    assert set([x["user_role_xref_id"] for x in response_data]) == set(
        access_grants_created
    )


def test_get_user_role_assignments_filtering_for_idir_delegated_admin(
    test_client_fixture,
    test_rsa_key,
    create_test_user_role_assignments,
    fom_dev_access_admin_token,
):
    """
    The test focus on filtering of the GET endpoint for application's user/role
    return (get_fam_application_user_role_assignment) for the delegated admin
    login user.

    The test uses application "FOM_DEV" and verifies login user who is IDIR
    user, not an appication admin but has DELEGATED_ADMIN role with specific
    scopes. This login user should be able to see user/role for both IDIR and
    BCEID users with scoped grants for a specific application.
    """
    # --- Prepare

    # Setup various user grants for different user_type(s), role_type(s),
    #   forest_client role scope and organizations.
    # Use these setup to verify visibility for the request user
    #   (DELEGATED_ADMIN - IDIR).
    access_grants_able_to_see = [
        ACCESS_GRANT_FOM_DEV_CR_IDIR,  # IDIR FOM_REVIEWER
        ACCESS_GRANT_FOM_DEV_CR_BCEID_L3T,  # BCEID FOM_REVIEWER L3T (org 1)
        ACCESS_GRANT_FOM_DEV_CR_BCEID_L4T,  # BCEID FOM_REVIEWER L4T (org 2)
        ACCESS_GRANT_FOM_DEV_AR_00001018_IDIR,  # IDIR FOM_SUBMITTER FC1
        ACCESS_GRANT_FOM_DEV_AR_00001018_BCEID_L3T,  # BCEID FOM_SUBMITTER FC1 L3T (org 1)
        ACCESS_GRANT_FOM_DEV_AR_00001018_BCEID_L4T,  # BCEID FOM_SUBMITTER FC1 L4T (org 2)
    ]
    access_grants_not_able_to_see = [
        ACCESS_GRANT_FOM_DEV_AR_00000001_IDIR,  # IDIR FOM_SUBMITTER FC2
    ]

    # --- Create users' access grants for FOM_DEV application.
    access_grants_can_see_created = create_test_user_role_assignments(
        fom_dev_access_admin_token, access_grants_able_to_see
    )

    access_grants_cannot_see_created = create_test_user_role_assignments(
        fom_dev_access_admin_token, access_grants_not_able_to_see
    )

    # Call GET endpoint with FOM_DEV DELEGATED_ADMIN user level to
    # obtain access grants for FOM_DEV application.
    #
    # Use 'COGNITO_USERNAME_IDIR_DELEGATED_ADMIN'. This user
    # "PTOLLEST"(IDIR)" has no FOM_DEV app admin role, but has delegated
    # admin privilege for FOM_REVIEWER and FORM_SUBMITTER_00001018, which is
    # granted in the local sql.
    token = jwt_utils.create_jwt_token(
        test_rsa_key, roles=[], username=jwt_utils.COGNITO_USERNAME_IDIR_DELEGATED_ADMIN
    )
    access_grants_response = test_client_fixture.get(
        get_application_role_assignment_end_point, headers=jwt_utils.headers(token)
    )
    response_data = access_grants_response.json().get("results")

    # --- Verify
    # This FOM_DEV IDIR DELEGATED_ADMIN admin user with FOM_REVIEWER and
    #   FOM_SUBMITTER_00001018 scoped roles should have visibility on user
    #   role assignments for both IDIR and BCEID users with FOM_REVIEWER and
    #   FOM_SUBMITTER_00001018 role.

    # verify access grants created result length is the same as
    #   access grants requested.
    assert len(access_grants_able_to_see) == len(access_grants_can_see_created)
    assert len(access_grants_not_able_to_see) == len(access_grants_cannot_see_created)

    # verify FOM_DEV IDIR delegated admin GET result contains exact set of
    #   user_role_xref_id from access_grants_can_see_created.
    assert set([x["user_role_xref_id"] for x in response_data]) == set(
        access_grants_can_see_created
    )

    # Verify this IDIR delegated admin can view # of records same as # records
    #   from what was setup to be seen.
    assert len(response_data) == len(access_grants_able_to_see)

    # Verify this IDIR delegated admin has privileges to view only for users
    #   granted with: FOM_REVIEWER, FOM_SUBMITTER_00001018
    assert all(
        granted["role"]["application"]["application_id"] == FOM_DEV_APPLICATION_ID
        and (
            granted["role"]["role_name"] == ROLE_NAME_FOM_REVIEWER
            or granted["role"]["role_name"] == ROLE_NAME_FOM_SUBMITTER_00001018
        )
        for granted in response_data
    )

    # Verify this IDIR delegated admin can view "IDIR" users for # of records
    #   matches what were granted with FOM_REVIEWER and FOM_SUBMITTER_00001018
    #   role.
    assert len(
        [
            data
            for data in response_data
            if (
                data["role"]["application"]["application_id"] == FOM_DEV_APPLICATION_ID
                and data["user"]["user_type"]["code"] == UserType.IDIR
            )
        ]
    ) == len(
        [
            grant
            for grant in access_grants_able_to_see
            if (grant["user_type_code"] == UserType.IDIR)
        ]
    )

    # Verify this IDIR delegated admin can view "BCEID" users for # of records
    #   matches what were granted with FOM_REVIEWER and FOM_SUBMITTER_00001018
    #   role.
    assert len(
        [
            data
            for data in response_data
            if (
                data["role"]["application"]["application_id"] == FOM_DEV_APPLICATION_ID
                and data["user"]["user_type"]["code"] == UserType.BCEID
            )
        ]
    ) == len(
        [
            grant
            for grant in access_grants_able_to_see
            if (grant["user_type_code"] == UserType.BCEID)
        ]
    )

    # Verify response does not contains this user grant:
    # "ACCESS_GRANT_FOM_DEV_AR_00000001_IDIR" in access_grants_not_able_to_see
    # list for this delegated admin who only can view FOM_REVIEWER and
    # FOM_SUBMITTER_00001018 role.
    assert (
        len(
            [
                data
                for data in response_data
                if (
                    data["role"]["application"]["application_id"]
                    == FOM_DEV_APPLICATION_ID
                    and data["user"]["user_type"]["code"] == UserType.IDIR
                    and data["role"]["role_name"] == ROLE_NAME_FOM_SUBMITTER_00000001
                )
            ]
        )
        == 0
    )


def test_get_user_role_assignments_filtering_for_bceid_delegated_admin(
    test_client_fixture,
    test_rsa_key,
    create_test_user_role_assignments,
    fom_dev_access_admin_token,
    override_depends__enforce_bceid_terms_conditions_guard,
):
    """
    The test focus on filtering of the GET endpoint for application's user/role
    return (get_fam_application_user_role_assignment) for the delegated admin
    login user.

    The test uses application "FOM_DEV" and verifies login user who is BCEID
    user, not an appication admin but has DELEGATED_ADMIN role with specific
    scopes. This login user should be able to see user/role for only BCEID
    users with scoped grants for a specific application and within its
    organization.
    """
    # --- Prepare

    # Setup various user grants for different user_type(s), role_type(s),
    #   forest_client role scope and organizations.
    # Use these setup to verify visibility for the request user
    #   (DELEGATED_ADMIN - BCEID).
    access_grants_able_to_see = [
        ACCESS_GRANT_FOM_DEV_CR_BCEID_L3T,  # BCEID FOM_REVIEWER L3T (org 1)
        ACCESS_GRANT_FOM_DEV_AR_00001018_BCEID_L3T,  # BCEID FOM_SUBMITTER FC1 L3T (org 1)
    ]
    access_grants_not_able_to_see = [
        ACCESS_GRANT_FOM_DEV_CR_IDIR,  # IDIR FOM_REVIEWER
        ACCESS_GRANT_FOM_DEV_CR_BCEID_L4T,  # BCEID FOM_REVIEWER L4T (org 2)
        ACCESS_GRANT_FOM_DEV_AR_00001018_IDIR,  # IDIR FOM_SUBMITTER FC1
        ACCESS_GRANT_FOM_DEV_AR_00000001_IDIR,  # IDIR FOM_SUBMITTER FC2
        ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID_L3T,  # BCEID FOM_SUBMITTER FC2 L3T (org 1)
        ACCESS_GRANT_FOM_DEV_AR_00001018_BCEID_L4T,  # BCEID FOM_SUBMITTER FC1 L4T (org 2)
    ]

    # --- Create users' access grants for FOM_DEV application.
    access_grants_can_see_created = create_test_user_role_assignments(
        fom_dev_access_admin_token, access_grants_able_to_see
    )
    access_grants_cannot_see_created = create_test_user_role_assignments(
        fom_dev_access_admin_token, access_grants_not_able_to_see
    )

    # override router guard dependencies
    override_depends__enforce_bceid_terms_conditions_guard()

    # Call GET endpoint with FOM_DEV DELEGATED_ADMIN user level to
    # obtain access grants for FOM_DEV application.
    #
    # Use 'COGNITO_USERNAME_BCEID_DELEGATED_ADMIN'. This user
    # "TEST-3-LOAD-CHILD-1" has no FOM_DEV app admin role, but has delegated
    # admin privilege for FOM_REVIEWER and FORM_SUBMITTER_00001018, which is
    # granted in the local sql. It also is the same organization as
    # "LOAD-3-TEST" user but not the same organization as "LOAD-4-TEST".
    token = jwt_utils.create_jwt_token(
        test_rsa_key,
        roles=[],
        username=jwt_utils.COGNITO_USERNAME_BCEID_DELEGATED_ADMIN,
    )
    access_grants_response = test_client_fixture.get(
        get_application_role_assignment_end_point, headers=jwt_utils.headers(token)
    )
    response_data = access_grants_response.json().get("results")

    # --- Verify
    # This FOM_DEV BCEID DELEGATED_ADMIN admin user with FOM_REVIEWER and
    #   FOM_SUBMITTER_00001018 scoped roles should have visibility on user
    #   role assignments for only "BCEID" users with FOM_REVIEWER and
    #   FOM_SUBMITTER_00001018 role, within the same organization.

    # verify access grants created result length is the same as
    #   access grants requested.
    assert len(access_grants_able_to_see) == len(access_grants_can_see_created)
    assert len(access_grants_not_able_to_see) == len(access_grants_cannot_see_created)

    # verify FOM_DEV BCEID delegated admin GET result contains exact set of
    #   user_role_xref_id from access_grants_can_see_created.
    assert set([x["user_role_xref_id"] for x in response_data]) == set(
        access_grants_can_see_created
    )

    # Verify this BCEID delegated admin has privileges to view only for BCEID
    #   users granted with: FOM_REVIEWER, FOM_SUBMITTER_00001018 and within
    #   the same organization.
    assert all(
        data["role"]["application"]["application_id"] == FOM_DEV_APPLICATION_ID
        and (
            data["role"]["role_name"] == ROLE_NAME_FOM_REVIEWER
            or data["role"]["role_name"] == ROLE_NAME_FOM_SUBMITTER_00001018
        )
        and data["user"]["user_type"]["code"] == UserType.BCEID
        and data["user"]["user_name"] == USER_NAME_BCEID_LOAD_3_TEST
        for data in response_data
    )

    # Verify this BCEID delegated admin cannot view "IDIR" users' grants.
    assert (
        len(
            [
                data
                for data in response_data
                if (
                    data["role"]["application"]["application_id"]
                    == FOM_DEV_APPLICATION_ID
                    and data["user"]["user_type"]["code"] == UserType.IDIR
                )
            ]
        )
        == 0
    )

    # Verify this BCEID delegated admin can view records exact matches what
    #   were granted in access_grants_able_to_see list [
    #   ACCESS_GRANT_FOM_DEV_CR_BCEID_L3T and
    #   ACCESS_GRANT_FOM_DEV_AR_00001018_BCEID_L3T]
    assert (
        len(
            [
                data
                for data in response_data
                if (
                    data["role"]["application"]["application_id"]
                    == FOM_DEV_APPLICATION_ID
                    and data["user"]["user_type"]["code"] == UserType.BCEID
                    and (
                        data["role"]["role_name"] == ROLE_NAME_FOM_REVIEWER
                        or data["role"]["role_name"] == ROLE_NAME_FOM_SUBMITTER_00001018
                    )
                    and data["user"]["user_name"] == USER_NAME_BCEID_LOAD_3_TEST
                )
            ]
        )
        == len(access_grants_able_to_see)
    ) and (len(response_data) == len(access_grants_able_to_see))


def test_get_fam_application_user_role_assignment_enforce_bceid_terms_conditions(
    test_client_fixture,
    test_rsa_key,
    db_pg_session,
    fom_dev_access_admin_token,
    create_test_user_role_assignments,
    get_current_requester_by_token,
):
    """
    Test this endpoint can "enforce_bceid_terms_conditions" on BCeID
    delegated admin requester when no T&C accepted (record in fam_user_terms_conditions).
    """
    # Use COGNITO_USERNAME_BCEID_DELEGATED_ADMIN as the requester "TEST-3-LOAD-CHILD-1"(BCEID),
    # who is a delegated admin for FOM_REVIEWER preset at database (flyway) but no T&C record.
    token = jwt_utils.create_jwt_token(
        test_rsa_key,
        roles=[],
        username=jwt_utils.COGNITO_USERNAME_BCEID_DELEGATED_ADMIN,
    )
    response = test_client_fixture.get(
        get_application_role_assignment_end_point, headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() is not None
    assert (
        str(response.json()["detail"]).find(ERROR_CODE_TERMS_CONDITIONS_REQUIRED) != -1
    )

    requester = get_current_requester_by_token(token)
    # create T&C record as the requester accepts T&C.
    db_pg_session.execute(
        insert(FamUserTermsConditions),
        [
            {
                "user_id": requester.user_id,
                "version": CURRENT_TERMS_AND_CONDITIONS_VERSION,
                "create_user": TEST_CREATOR,
            }
        ],
    )

    response = test_client_fixture.get(
        get_application_role_assignment_end_point, headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.OK


def test_get_application_user_by_id_success(
    test_client_fixture: starlette.testclient.TestClient, test_rsa_key
):
    """
    Test the GET /{application_id}/users/{user_id} endpoint for valid user data retrieval.
    """
    application_id = FOM_DEV_APPLICATION_ID
    user_id = TEST_USER_ID

    token = jwt_utils.create_jwt_token(test_rsa_key, ACCESS_ROLES_FOM_DEV_ONLY)

    response = test_client_fixture.get(
        end_point_user_by_id.format(application_id=application_id, user_id=user_id),
        headers=jwt_utils.headers(token),
    )

    assert response.status_code == HTTPStatus.OK
    data = response.json()

    assert "user_name" in data
    assert "first_name" in data


def test_get_application_user_by_id_not_found(
    test_client_fixture: starlette.testclient.TestClient, test_rsa_key
):
    """
    Test the GET /{application_id}/users/{user_id} endpoint for a non-existent user.
    """
    application_id = FOM_DEV_APPLICATION_ID
    user_id = NOT_EXIST_TEST_USER_ID

    token = jwt_utils.create_jwt_token(test_rsa_key, ACCESS_ROLES_FOM_DEV_ONLY)

    response = test_client_fixture.get(
        end_point_user_by_id.format(application_id=application_id, user_id=user_id),
        headers=jwt_utils.headers(token),
    )

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_get_application_user_by_id_application_authorization(
    test_client_fixture: starlette.testclient.TestClient, test_rsa_key
):
    """
    Test the GET /{application_id}/users/{user_id} endpoint for application authorization.
    """
    application_id = FOM_DEV_APPLICATION_ID
    user_id = TEST_USER_ID

    # Create a token for a user who does not have access to the application
    unauthorized_token = jwt_utils.create_jwt_token(test_rsa_key, [NOT_EXIST_ROLE_NAME])

    response = test_client_fixture.get(
        end_point_user_by_id.format(application_id=application_id, user_id=user_id),
        headers=jwt_utils.headers(unauthorized_token),
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.parametrize(
    "invalid_page_params",
    [
        {"pageNumber":0, "pageSize": 10},
        {"pageNumber":1, "pageSize": 10000000},
        {"pageNumber":"invalid"},
        {"pageSize":"invalid"},
        {"sortBy": "invalid_column", "sortOrder": "asc"},
        {"sortBy": "user_name", "sortOrder": "invalid_sort_order"},
        {"search":"long_search_string_exceeds_maximum_search_length"},
    ]
)
def test_get_fam_application_user_role_assignment__pagining_with_invalid_page_params(
    mocker, test_client_fixture,
    get_fam_application_user_role_assignment_dependencies_override,
    test_rsa_key, invalid_page_params
):
    mocker.patch(
        "api.app.routers.router_application.crud_application.get_application_role_assignments",
        return_value=[],
    )
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        get_application_role_assignment_end_point, headers=jwt_utils.headers(token),
        params=invalid_page_params
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_get_fam_application_user_role_assignment__pagining_with_valid_page_params_result_success(
    mocker, test_client_fixture,
    get_fam_application_user_role_assignment_dependencies_override,
    test_rsa_key
):
    mocker.patch(
        "api.app.routers.router_application.crud_application.get_application_role_assignments",
        return_value=APP_USER_ROLE_PAGED_RESULT_2_RECORDS,
    )
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        get_application_role_assignment_end_point, headers=jwt_utils.headers(token),
        params={"pageNumber":1, "pageSize": 10}  # valid page_params
    )
    assert response.status_code == HTTPStatus.OK


def test_get_fam_application_user_role_assignment__no_params_in_request_then_use_defaults_result_success(
    test_client_fixture,
    get_fam_application_user_role_assignment_dependencies_override,
    test_rsa_key
):
    """
    This test tests a particular case when request does not provide sorting params then router should
    automatically gets defaults values (if any). In this case of page_params should be supplied to
    "crud_application.get_application_role_assignments()" method with "default" page_params attributes.

    Python Mock library does not seem to provide an easy way (or documented) to restore back the method
    being mocked. The easy way is to get the original method reference -> mock the method -> then
    reassign the method reference back to original method.

    Example:
        original_fn = crud_application.get_application_role_assignments
        crud_application.get_application_role_assignments = Mock(...)
        ...
        ... do some testing and verify with the mock
        ...
        crud_application.get_application_role_assignments = original_fn

        ref: https://discuss.python.org/t/right-way-to-use-reset-mock/58427/2
    """
    original_fn = crud_application.get_application_role_assignments
    crud_application.get_application_role_assignments = Mock(return_value=APP_USER_ROLE_PAGED_RESULT_2_RECORDS)

    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        get_application_role_assignment_end_point, headers=jwt_utils.headers(token)
    )

    assert response.status_code == HTTPStatus.OK
    # pytest has somewhat difficult way to assert arguments being called at mock.
    # see ref: https://docs.python.org/3.3/library/unittest.mock.html#unittest.mock.Mock.call_args
    mock_fn_call_args = crud_application.get_application_role_assignments.call_args

    # validate defaults are provided when no request param is in the request.
    assert mock_fn_call_args[1]["page_params"] == UserRolePageParamsSchema(
        page=MIN_PAGE, size=DEFAULT_PAGE_SIZE, search=None,
        sort_order=SortOrderEnum.DESC, sort_by=UserRoleSortByEnum.CREATE_DATE
    )

    # !! Below line is very important (to restor the method from mock) for not to interfere subsequent tests cases.
    crud_application.get_application_role_assignments = original_fn


def test_export_application_user_roles_success(
    mocker,
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    get_fam_application_user_role_assignment_dependencies_override,
):
    """
    Test the export_application_user_roles endpoint for successful CSV export.
    """
    mock_results = [
        Mock(
            role=Mock(
                application=Mock(application_name="TestApp"),
                display_name="TestRole",
                forest_client=None,
            ),
            user=Mock(
                user_name="test_user",
                user_type_relation=Mock(description="TestDomain"),
                first_name="Test",
                last_name="User",
                email="test_user@example.com",
            ),
            create_date=Mock(strftime=lambda fmt: "2023-01-01"),
        )
    ]

    mocker.patch(
        "api.app.routers.router_application.crud_application.get_application_role_assignments_no_paging",
        return_value=mock_results,
    )

    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(
        f"{get_application_role_assignment_end_point}/export",
        headers=jwt_utils.headers(token),
    )

    assert response.status_code == HTTPStatus.OK
    assert "text/csv" in response.headers["Content-Type"].lower()
    assert "Content-Disposition" in response.headers
    filename = response.headers["Content-Disposition"].split("=")[1]
    assert ".csv" in filename


def test_export_application_user_roles_unauthorized(
    test_client_fixture: starlette.testclient.TestClient, test_rsa_key
):
    """
    Test the export_application_user_roles endpoint for unauthorized access.
    """
    unauthorized_token = jwt_utils.create_jwt_token(test_rsa_key, [NOT_EXIST_ROLE_NAME])

    response = test_client_fixture.get(
        f"{get_application_role_assignment_end_point}/export",
        headers=jwt_utils.headers(unauthorized_token),
    )

    assert response.status_code == HTTPStatus.FORBIDDEN


def test_export_application_user_roles_has_necessary_authorizeaton_guard_checks():
    """
    Test that the export_application_user_roles endpoint has authorization guards in place.
    This test verifies that the endpoint is protected by the 'authorize_by_app_id' and
    'enforce_bceid_terms_conditions_guard' dependencies.
    """
    route = next(
        (route for route in router.routes if route.path == "/{application_id}/user-role-assignment/export"),
        None,
    )
    assert route is not None
    assert any(
        dependency.dependency == authorize_by_app_id for dependency in route.dependencies
    ), "authorize_by_app_id check should be a dependency for export_application_user_roles"
    assert any(
        dependency.dependency == enforce_bceid_terms_conditions_guard for dependency in route.dependencies
    ), "enforce_bceid_terms_conditions_guard check should be a dependency for export_application_user_roles"