import logging
from http import HTTPStatus

import starlette.testclient
import testspg.jwt_utils as jwt_utils
from api.app.main import apiPrefix
from api.app.constants import ERROR_CODE_INVALID_APPLICATION_ID, UserType
from testspg.constants import (
    FC_NUMBER_EXISTS_ACTIVE_00001011,
    FC_NUMBER_EXISTS_ACTIVE_00001018,
    FOM_DEV_APPLICATION_ID,
    ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID,
    ACCESS_GRANT_FOM_DEV_AR_00001018_BCEID_L3T,
    ACCESS_GRANT_FOM_DEV_AR_00001018_BCEID_L4T,
    ACCESS_GRANT_FOM_DEV_AR_00000001_IDIR,
    ACCESS_GRANT_FOM_DEV_CR_BCEID_L3T,
    ACCESS_GRANT_FOM_DEV_CR_BCEID_L4T,
    ACCESS_GRANT_FOM_DEV_CR_IDIR,
    FOM_DEV_REVIEWER_ROLE_ID,
    FOM_DEV_SUBMITTER_ROLE_ID,
    ROLE_NAME_FOM_REVIEWER,
    ROLE_NAME_FOM_SUBMITTER_00001018,
    USER_NAME_BCEID_LOAD_3_TEST)

LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/fam_applications"

TEST_APPLICATION_NAME_FOM_DEV = "FOM_DEV"
TEST_APPLICATION_ROLES_FOM_DEV = ["FOM_SUBMITTER", "FOM_REVIEWER"]
TEST_APPLICATION_ID_NOT_FOUND = 0


def test_get_applications(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key
):
    # Test Accss Roles: FAM_ADMIN only
    access_roles_fam_only = ["FAM_ADMIN"]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fam_only)
    response = test_client_fixture.get(f"{endPoint}", headers=jwt_utils.headers(token))
    data = response.json()
    assert len(data) == 1
    assert data[0]["application_name"] == "FAM"

    # Test Accss Roles: FOM_DEV_ADMIN only
    access_roles_fom_dev_only = ["FOM_DEV_ADMIN"]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fom_dev_only)
    response = test_client_fixture.get(f"{endPoint}", headers=jwt_utils.headers(token))
    data = response.json()
    assert len(data) == 1
    assert data[0]["application_name"] == "FOM_DEV"

    # Test Accss Roles: both FAM_ADMIN and FOM_DEV_ADMIN
    access_roles_fam_fom_dev = ["FAM_ADMIN", "FOM_DEV_ADMIN"]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fam_fom_dev)
    response = test_client_fixture.get(f"{endPoint}", headers=jwt_utils.headers(token))
    data = response.json()
    assert len(data) == 2
    assert data[0]["application_name"] == "FAM"
    assert data[1]["application_name"] == "FOM_DEV"
    # verify it got all attributes
    for app in data:
        assert "application_id" in app
        assert "application_name" in app
        assert "application_description" in app
        assert "create_user" in app
        assert "create_date" in app
        assert "update_user" in app
        assert "update_date" in app
        assert "app_environment" in app

    # Test Accss Roles: on NO_APP_ADMIN
    access_roles_no_app = ["NO_APP_ADMIN"]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_no_app)
    response = test_client_fixture.get(f"{endPoint}", headers=jwt_utils.headers(token))
    data = response.json()
    assert len(data) == 0


def test_get_fam_application_roles(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key
):
    # create a concrete role with an abstract role as parent
    # this role won't be returned
    access_roles_fom_dev_only = ["FOM_DEV_ADMIN"]
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fom_dev_only)

    response = test_client_fixture.post(
        f"{apiPrefix}/user_role_assignment",
        json=ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID,
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 200

    role_end_point = endPoint + f"/{FOM_DEV_APPLICATION_ID}/fam_roles"
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fom_dev_only)
    response = test_client_fixture.get(role_end_point, headers=jwt_utils.headers(token))
    data = response.json()
    # only return roles without a parent role
    assert len(data) == 2

    for app_role in data:
        assert "role_id" in app_role
        assert "role_name" in app_role
        assert "role_purpose" in app_role
        assert "parent_role_id" in app_role
        assert "application_id" in app_role
        assert "forest_client_number" in app_role
        assert "client_number" in app_role
        assert "role_type_code" in app_role

    fom_reviewer_role_found = False
    fom_submitter_role_found = False

    for datum in data:
        if (
            datum["role_name"] == TEST_APPLICATION_ROLES_FOM_DEV[0]
            and datum["application_id"] == FOM_DEV_APPLICATION_ID
            and datum["role_type_code"] == "A"
        ):
            fom_submitter_role_found = True
        elif (
            datum["role_name"] == TEST_APPLICATION_ROLES_FOM_DEV[1]
            and datum["application_id"] == FOM_DEV_APPLICATION_ID
            and datum["role_type_code"] == "C"
        ):
            fom_reviewer_role_found = True

    assert fom_submitter_role_found, f"Expected role {TEST_APPLICATION_ROLES_FOM_DEV[0]} in results"
    assert fom_reviewer_role_found, f"Expected role {TEST_APPLICATION_ROLES_FOM_DEV[1]} in results"


def test_get_fam_application_user_role_assignment_no_matching_application(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key
):
    role_assignment_end_point = endPoint + \
        f"/{TEST_APPLICATION_ID_NOT_FOUND}/user_role_assignment"
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.get(role_assignment_end_point,
                                       headers=jwt_utils.headers(token))
    data = response.json()
    assert data["detail"]["code"] == ERROR_CODE_INVALID_APPLICATION_ID


def test_get_fam_application_user_role_assignment_no_role_assignments(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key
):
    access_roles_fom_dev_only = ["FOM_DEV_ADMIN"]

    # test no user role assignment for the application
    role_assignment_end_point = endPoint + \
        f"/{FOM_DEV_APPLICATION_ID}/user_role_assignment"
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fom_dev_only)
    response = test_client_fixture.get(role_assignment_end_point,
                                       headers=jwt_utils.headers(token))
    data = response.json()
    assert len(data) == 0  # initially no one is assigned with FOM_DEV roles


def test_get_fam_application_user_role_assignment_concrete_role(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key
):
    access_roles_fom_dev_only = ["FOM_DEV_ADMIN"]

    role_assignment_end_point = endPoint + \
        f"/{FOM_DEV_APPLICATION_ID}/user_role_assignment"

    # test user role assignment
    # create
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fom_dev_only)
    response = test_client_fixture.post(
        f"{apiPrefix}/user_role_assignment",
        json=ACCESS_GRANT_FOM_DEV_CR_IDIR,
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 200
    concrete_role_data = response.json()

    # check
    response = test_client_fixture.get(role_assignment_end_point,
                                       headers=jwt_utils.headers(token))
    data = response.json()
    assert len(data) == 1
    assert data[0]["user_role_xref_id"] == concrete_role_data["user_role_xref_id"]
    assert data[0]["user"]["user_type_code"] \
        == ACCESS_GRANT_FOM_DEV_CR_IDIR["user_type_code"]
    assert data[0]["user"]["user_name"] \
        == ACCESS_GRANT_FOM_DEV_CR_IDIR["user_name"]
    assert data[0]["role"]["role_type_code"] == "C"
    assert data[0]["role"]["role_name"] == "FOM_REVIEWER"


def test_get_fam_application_user_role_assignment_abstract_role(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key
):
    access_roles_fom_dev_only = ["FOM_DEV_ADMIN"]

    role_assignment_end_point = endPoint + \
        f"/{FOM_DEV_APPLICATION_ID}/user_role_assignment"

    # test user role assignment for abstract role
    # create
    token = jwt_utils.create_jwt_token(test_rsa_key, access_roles_fom_dev_only)
    response = test_client_fixture.post(
        f"{apiPrefix}/user_role_assignment",
        json=ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID,
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == 200
    abstract_role_data = response.json()

    # check
    response = test_client_fixture.get(role_assignment_end_point,
                                       headers=jwt_utils.headers(token))
    data = response.json()
    assert len(data) == 1
    assert data[0]["user_role_xref_id"] == abstract_role_data["user_role_xref_id"]
    assert data[0]["user"]["user_type_code"] \
        == ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID["user_type_code"]
    assert data[0]["user"]["user_name"] \
        == ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID["user_name"]
    assert data[0]["role"]["role_type_code"] == "C"
    assert data[0]["role"]["role_name"] == "FOM_SUBMITTER" + "_" + \
        ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID["forest_client_number"]
    assert data[0]["role"]["parent_role"]["role_type_code"] == "A"
    assert data[0]["role"]["parent_role"]["role_name"] == "FOM_SUBMITTER"


def test_fam_application_endpoints_invlid_path_application_id_type(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key
):
    token = jwt_utils.create_jwt_token(test_rsa_key)
    # endpoint path /{application_id} should be int type, provided as invalid str type.
    invalid_path_param = "not-int-str-application-id"
    invalid_path_router_msg = "Input should be a valid integer"

    # endpont GET: /{application_id}/fam_roles
    application_role_endpoint = endPoint + f"/{invalid_path_param}/fam_roles"
    response = test_client_fixture.get(
        application_role_endpoint,
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert invalid_path_router_msg in response.text

    # endpont GET: /{application_id}/user_role_assignment
    application_role_assignment_endpoint = endPoint + \
        f"/{invalid_path_param}/user_role_assignment"
    response = test_client_fixture.get(
        application_role_assignment_endpoint,
        headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert invalid_path_router_msg in response.text


# ---------------- Test get application user role assignment filtering scenarios ------------ #

def test_get_application_user_role_assignments_filtering_for_delegated_admin(
    test_client_fixture,
    test_rsa_key,
    create_test_user_role_assignments,
    fom_dev_access_admin_token,
):
    """
    This test first create various user role assigments at FOM_DEV (IDIR/BCEID,
    business organizations and forest client...) and verify different
    visibility scenarios based on requester's admin level and
    delegated admin privileges.
    """

    # --- Prepare
    # Assign IDIR test user to FOM_DEV app: FOM_REVIEWER and FOM_SUBMITTER roles.
    fom_dev_idir_access_grants = [
        ACCESS_GRANT_FOM_DEV_CR_IDIR,           # FOM_REVIEWER
        ACCESS_GRANT_FOM_DEV_AR_00000001_IDIR   # FOM_SUBMITTER
    ]
    # Assign BCEID users to FOM_DEV app: FOM_REVIEWER role.
    # Two users (LOAD-3-TEST, LOAD-4-TEST) belong to two different organizations.
    fom_dev_bceid_reviewer_access_grants = [
        ACCESS_GRANT_FOM_DEV_CR_BCEID_L3T,  # BCEID user L3T (org 1)
        ACCESS_GRANT_FOM_DEV_CR_BCEID_L4T   # BCEID user L4T (org 2)
    ]
    # Assign BCEID users (LOAD-3-TEST, LOAD-4-TEST) to FOM_DEV FOM_SUBMITTER
    #   with the same role (forest client: 00001018)
    # Two users (LOAD-3-TEST, LOAD-4-TEST) belong to two different organizations.
    fom_dev_bceid_submitters_00001018_access_grants = [
        ACCESS_GRANT_FOM_DEV_AR_00001018_BCEID_L3T,  # BCEID user L3T (org 1)
        ACCESS_GRANT_FOM_DEV_AR_00001018_BCEID_L4T   # BCEID user L4T (org 2)
    ]
    # Also only assign BCEID user (LOAD-3-TEST) to FOM_DEV FOM_SUBMITTER
    # with forest client 00001011
    USERR_ASGNMNT_FOM_DEV_AR_00001011_BCEID_L3T = \
        dict(ACCESS_GRANT_FOM_DEV_AR_00001018_BCEID_L3T)  # copy object
    USERR_ASGNMNT_FOM_DEV_AR_00001011_BCEID_L3T["forest_client_number"] = \
        FC_NUMBER_EXISTS_ACTIVE_00001011
    fom_dev_bceid_submitter_00001011_access_grants = [USERR_ASGNMNT_FOM_DEV_AR_00001011_BCEID_L3T]

    # --- Create users' access grants for FOM_DEV
    fom_dev_user_role_assignments_created = create_test_user_role_assignments(
        fom_dev_access_admin_token,
        fom_dev_idir_access_grants +
        fom_dev_bceid_reviewer_access_grants +
        fom_dev_bceid_submitters_00001018_access_grants +
        fom_dev_bceid_submitter_00001011_access_grants
    )

    # --- Verify created users' access grants for FOM_DEV

    # verify created result length is the same as access requested
    assert len(fom_dev_user_role_assignments_created) == (
        len(fom_dev_idir_access_grants) +
        len(fom_dev_bceid_reviewer_access_grants) +
        len(fom_dev_bceid_submitters_00001018_access_grants) +
        len(fom_dev_bceid_submitter_00001011_access_grants)
    )

    # View filtering results: GET enpoint for users' access grants.
    # ("{apiPrefix}/fam_applications/{application_id}/user_role_assignment")
    get_role_assignment_end_point = (
        endPoint + f"/{FOM_DEV_APPLICATION_ID}/user_role_assignment"
    )

    # verify: FOM_DEV_ADMIN has visibility for FOM_DEV
    #         all user role assignments.
    token = fom_dev_access_admin_token
    fom_dev_admin_user_access_grants_response = test_client_fixture.get(
        get_role_assignment_end_point, headers=jwt_utils.headers(token)
    )

    fom_dev_admin_rs_data = fom_dev_admin_user_access_grants_response.json()
    # verify FOM_DEV_ADMIN GET result contains exact set of user_role_xref_id
    #   from assigned user role assignments.
    assert len(fom_dev_admin_rs_data) == len(fom_dev_user_role_assignments_created)
    assert (
        set([x["user_role_xref_id"] for x in fom_dev_admin_rs_data]) ==
        set(fom_dev_user_role_assignments_created)
    )

    # verify: IDIR FOM_DEV (application) delegated admin with FOM_REVIEWER
    #         and FOM_SUBMITTER_00001018 roles has visibility on user role
    #         assignments for both IDIR and BCEID users with FOM_REVIEWER and
    #         FOM_SUBMITTER_00001018 role.

    # Use 'COGNITO_USERNAME_IDIR'. this user has no FOM_DEV app admin role,
    # but has delegated admin privilege for FOM_REVIEWER and
    # FORM_SUBMITTER_00001018, which is granted in the local sql.
    token = jwt_utils.create_jwt_token(
        test_rsa_key,
        roles=[],
        username=jwt_utils.COGNITO_USERNAME_IDIR_DELEGATED_ADMIN
    )
    fom_dev_idir_dgadmin_user_access_grants_response = test_client_fixture.get(
        get_role_assignment_end_point, headers=jwt_utils.headers(token)
    )
    fom_dev_idir_dgadmin_rs_data = fom_dev_idir_dgadmin_user_access_grants_response.json()
    fom_dev_idir_access_grants_for_reviewer = [
        grant for grant in fom_dev_idir_access_grants
        if grant["role_id"] == FOM_DEV_REVIEWER_ROLE_ID
    ]
    # this idir user should only see user access granted only for FOM_DEV
    # FOM_REVIEWER and FORM_SUBMITTER_00001018 role, not FORM_SUBMITTER_00000001
    # or FORM_SUBMITTER_00001011.
    assert len(fom_dev_idir_dgadmin_rs_data) == (
        len(fom_dev_idir_access_grants_for_reviewer) +
        len(fom_dev_bceid_reviewer_access_grants) +
        len(fom_dev_bceid_submitters_00001018_access_grants)
    )
    assert all(
        granted["role"]["application_id"] == FOM_DEV_APPLICATION_ID and
        (granted["role"]["role_name"] == ROLE_NAME_FOM_REVIEWER or
         granted["role"]["role_name"] == ROLE_NAME_FOM_SUBMITTER_00001018)
        for granted in fom_dev_idir_dgadmin_rs_data
    )
    assert len([granted for granted in fom_dev_idir_dgadmin_rs_data if (
        granted["role"]["application_id"] == FOM_DEV_APPLICATION_ID and
        granted["user"]["user_type_code"] == UserType.IDIR and
        granted["role"]["role_name"] == ROLE_NAME_FOM_REVIEWER
    )]) == len(fom_dev_idir_access_grants_for_reviewer)
    assert len([granted for granted in fom_dev_idir_dgadmin_rs_data if (
        granted["role"]["application_id"] == FOM_DEV_APPLICATION_ID and
        granted["user"]["user_type_code"] == UserType.BCEID and
        granted["role"]["role_name"] == ROLE_NAME_FOM_REVIEWER
    )]) == len(fom_dev_bceid_reviewer_access_grants)
    assert len([granted for granted in fom_dev_idir_dgadmin_rs_data if (
        granted["role"]["application_id"] == FOM_DEV_APPLICATION_ID and
        granted["user"]["user_type_code"] == UserType.BCEID and
        granted["role"]["role_name"] == ROLE_NAME_FOM_SUBMITTER_00001018
    )]) == len(fom_dev_bceid_submitters_00001018_access_grants)

    # verify: BCEID FOM_DEV (application) delegated admin with FOM_REVIEWER
    #         and FOM_SUBMITTER_00001018 roles has visibility on user role
    #         assignments for only BCEID users with FOM_REVIEWER and
    #         FOM_SUBMITTER_00001018 role, for the same organization.

    # Use 'COGNITO_USERNAME_BCEID'. this user "TEST-3-LOAD-CHILD-1" has no
    # FOM_DEV app admin role, but has delegated admin privilege for FOM_REVIEWER
    # and FORM_SUBMITTER_00001018, which is granted in the local sql. It also
    # is the same organization as "LOAD-3-TEST" user but not the same
    # organization as "LOAD-4-TEST".
    token = jwt_utils.create_jwt_token(
        test_rsa_key,
        roles=[],
        username=jwt_utils.COGNITO_USERNAME_BCEID_DELEGATED_ADMIN
    )
    fom_dev_bceid_dgadmin_user_access_grants_response = test_client_fixture.get(
        get_role_assignment_end_point, headers=jwt_utils.headers(token)
    )
    fom_dev_bceid_dgadmin_rs_data = fom_dev_bceid_dgadmin_user_access_grants_response.json()
    # this BCEID delegated admin should only see user access granted for
    # FOM_DEV FOM_REVIEWER and FORM_SUBMITTER_00001018 role for BCEID users,
    # within its organization, not FORM_SUBMITTER_00000001 or
    # FORM_SUBMITTER_00001011.
    fom_dev_bceid_access_grants_for_reviewer_l3t = [
        grant for grant in fom_dev_bceid_reviewer_access_grants
        if grant["role_id"] == FOM_DEV_REVIEWER_ROLE_ID and
        grant["user_name"] == USER_NAME_BCEID_LOAD_3_TEST
    ]
    fom_dev_bceid_submitters_00001018_access_grants_l3t = [
        grant for grant in fom_dev_bceid_submitters_00001018_access_grants
        if grant["role_id"] == FOM_DEV_SUBMITTER_ROLE_ID and
        grant["user_name"] == USER_NAME_BCEID_LOAD_3_TEST and
        grant["forest_client_number"] == FC_NUMBER_EXISTS_ACTIVE_00001018
    ]
    assert len(fom_dev_bceid_dgadmin_rs_data) == (
        len(fom_dev_bceid_access_grants_for_reviewer_l3t) +
        len(fom_dev_bceid_submitters_00001018_access_grants_l3t)
    )
    assert all(
        granted["role"]["application_id"] == FOM_DEV_APPLICATION_ID and
        (granted["role"]["role_name"] == ROLE_NAME_FOM_REVIEWER or
         granted["role"]["role_name"] == ROLE_NAME_FOM_SUBMITTER_00001018) and
        granted["user"]["user_type_code"] == UserType.BCEID and
        granted["user"]["user_name"] == USER_NAME_BCEID_LOAD_3_TEST
        for granted in fom_dev_bceid_dgadmin_rs_data
    )
    assert len([granted for granted in fom_dev_bceid_dgadmin_rs_data if (
        granted["role"]["application_id"] == FOM_DEV_APPLICATION_ID and
        granted["user"]["user_type_code"] == UserType.BCEID and
        granted["role"]["role_name"] == ROLE_NAME_FOM_REVIEWER and
        granted["user"]["user_name"] == USER_NAME_BCEID_LOAD_3_TEST
    )]) == len(fom_dev_bceid_access_grants_for_reviewer_l3t)
    assert len([granted for granted in fom_dev_bceid_dgadmin_rs_data if (
        granted["role"]["application_id"] == FOM_DEV_APPLICATION_ID and
        granted["user"]["user_type_code"] == UserType.BCEID and
        granted["role"]["role_name"] == ROLE_NAME_FOM_SUBMITTER_00001018 and
        granted["user"]["user_name"] == USER_NAME_BCEID_LOAD_3_TEST
    )]) == len(fom_dev_bceid_submitters_00001018_access_grants_l3t)
