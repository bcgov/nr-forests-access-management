import logging
from http import HTTPStatus

import starlette.testclient
import testspg.jwt_utils as jwt_utils
from api.app.constants import ERROR_CODE_INVALID_APPLICATION_ID, UserType
from api.app.main import apiPrefix
from testspg.constants import (ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID,
                               ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID_L3T,
                               ACCESS_GRANT_FOM_DEV_AR_00000001_IDIR,
                               ACCESS_GRANT_FOM_DEV_AR_00001018_BCEID_L3T,
                               ACCESS_GRANT_FOM_DEV_AR_00001018_BCEID_L4T,
                               ACCESS_GRANT_FOM_DEV_AR_00001018_IDIR,
                               ACCESS_GRANT_FOM_DEV_CR_BCEID_L3T,
                               ACCESS_GRANT_FOM_DEV_CR_BCEID_L4T,
                               ACCESS_GRANT_FOM_DEV_CR_IDIR,
                               FOM_DEV_APPLICATION_ID, ROLE_NAME_FOM_REVIEWER,
                               ROLE_NAME_FOM_SUBMITTER_00000001,
                               ROLE_NAME_FOM_SUBMITTER_00001018,
                               USER_NAME_BCEID_LOAD_3_TEST)

LOGGER = logging.getLogger(__name__)
end_point = f"{apiPrefix}/fam_applications"

# GET enpoint for users' access grants.
# ("{apiPrefix}/fam_applications/{application_id}/user_role_assignment")
get_application_role_assignment_end_point = (
    end_point + f"/{FOM_DEV_APPLICATION_ID}/user_role_assignment"
)

TEST_APPLICATION_NAME_FOM_DEV = "FOM_DEV"
TEST_APPLICATION_ROLES_FOM_DEV = ["FOM_SUBMITTER", "FOM_REVIEWER"]
TEST_APPLICATION_ID_NOT_FOUND = 0


def test_get_fam_application_user_role_assignment_no_matching_application(
    test_client_fixture: starlette.testclient.TestClient, test_rsa_key
):
    role_assignment_end_point = (
        end_point + f"/{TEST_APPLICATION_ID_NOT_FOUND}/user_role_assignment"
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
    access_roles_fom_dev_only = ["FOM_DEV_ADMIN"]

    # test no user role assignment for the application
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fom_dev_only)
    response = test_client_fixture.get(
        get_application_role_assignment_end_point, headers=jwt_utils.headers(token)
    )
    data = response.json()
    assert len(data) == 0  # initially no one is assigned with FOM_DEV roles


def test_get_fam_application_user_role_assignment_concrete_role(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    override_get_verified_target_user,
):
    access_roles_fom_dev_only = ["FOM_DEV_ADMIN"]

    # override router guard dependencies
    override_get_verified_target_user()

    # test user role assignment
    # create
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fom_dev_only)
    response = test_client_fixture.post(
        f"{apiPrefix}/user_role_assignment",
        json=ACCESS_GRANT_FOM_DEV_CR_IDIR,
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == 200
    concrete_role_data = response.json()

    # check
    response = test_client_fixture.get(
        get_application_role_assignment_end_point, headers=jwt_utils.headers(token)
    )
    data = response.json()
    assert len(data) == 1
    assert data[0]["user_role_xref_id"] == concrete_role_data["user_role_xref_id"]
    assert (
        data[0]["user"]["user_type_code"]
        == ACCESS_GRANT_FOM_DEV_CR_IDIR["user_type_code"]
    )
    assert data[0]["user"]["user_name"] == ACCESS_GRANT_FOM_DEV_CR_IDIR["user_name"]
    assert data[0]["role"]["role_type_code"] == "C"
    assert data[0]["role"]["role_name"] == "FOM_REVIEWER"


def test_get_fam_application_user_role_assignment_abstract_role(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    override_get_verified_target_user,
):
    access_roles_fom_dev_only = ["FOM_DEV_ADMIN"]

    # override router guard dependencies
    override_get_verified_target_user(ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID)

    # test user role assignment for abstract role
    # create
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fom_dev_only)
    response = test_client_fixture.post(
        f"{apiPrefix}/user_role_assignment",
        json=ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID,
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == 200
    abstract_role_data = response.json()

    # check
    response = test_client_fixture.get(
        get_application_role_assignment_end_point, headers=jwt_utils.headers(token)
    )
    data = response.json()
    assert len(data) == 1
    assert data[0]["user_role_xref_id"] == abstract_role_data["user_role_xref_id"]
    assert (
        data[0]["user"]["user_type_code"]
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
        + ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID["forest_client_number"]
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

    # endpont GET: /{application_id}/user_role_assignment
    application_role_assignment_endpoint = (
        end_point + f"/{invalid_path_param}/user_role_assignment"
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
    response_data = access_grants_response.json()

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
    response_data = access_grants_response.json()

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
        granted["role"]["application_id"] == FOM_DEV_APPLICATION_ID
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
                data["role"]["application_id"] == FOM_DEV_APPLICATION_ID
                and data["user"]["user_type_code"] == UserType.IDIR
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
                data["role"]["application_id"] == FOM_DEV_APPLICATION_ID
                and data["user"]["user_type_code"] == UserType.BCEID
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
                    data["role"]["application_id"] == FOM_DEV_APPLICATION_ID
                    and data["user"]["user_type_code"] == UserType.IDIR
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
    override_enforce_bceid_terms_conditions_guard
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
    override_enforce_bceid_terms_conditions_guard()

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
    response_data = access_grants_response.json()

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
        data["role"]["application_id"] == FOM_DEV_APPLICATION_ID
        and (
            data["role"]["role_name"] == ROLE_NAME_FOM_REVIEWER
            or data["role"]["role_name"] == ROLE_NAME_FOM_SUBMITTER_00001018
        )
        and data["user"]["user_type_code"] == UserType.BCEID
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
                    data["role"]["application_id"] == FOM_DEV_APPLICATION_ID
                    and data["user"]["user_type_code"] == UserType.IDIR
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
                    data["role"]["application_id"] == FOM_DEV_APPLICATION_ID
                    and data["user"]["user_type_code"] == UserType.BCEID
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
