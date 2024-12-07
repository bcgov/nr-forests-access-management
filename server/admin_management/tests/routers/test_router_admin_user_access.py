import logging
from http import HTTPStatus

import starlette.testclient
import tests.jwt_utils as jwt_utils
from api.app.constants import AdminRoleAuthGroup, AppEnv, RoleType
from api.app.main import apiPrefix
from tests.constants import (TEST_APP_FOM_NAME,
                             TEST_APP_ROLE_NAME_FOM_REVIEWER,
                             TEST_APP_ROLE_NAME_FOM_SUBMITTER,
                             TEST_APPLICATION_ID_FAM,
                             TEST_APPLICATION_ID_FOM_DEV,
                             TEST_APPLICATION_ID_FOM_TEST,
                             TEST_APPLICATION_NAME_FAM,
                             TEST_DUMMY_COGNITO_USER_ID,
                             TEST_FOM_DEV_REVIEWER_ROLE_ID,
                             TEST_FOM_DEV_SUBMITTER_ROLE_ID,
                             TEST_FOM_TEST_REVIEWER_ROLE_ID,
                             TEST_FOM_TEST_SUBMITTER_ROLE_ID,
                             TEST_FOREST_CLIENT_NUMBER,
                             TEST_FOREST_CLIENT_NUMBER_TWO,
                             TEST_NEW_BCEID_USER, TEST_NEW_IDIR_USER)

LOGGER = logging.getLogger(__name__)
test_end_point = f"{apiPrefix}/admin-user-accesses"

# Below tests are based on endpoint json sample output at confluence design:
# https://apps.nrs.gov.bc.ca/int/confluence/display/FSAST1/Delegated+Access+Administration+Design


def test_get_admin_user_access__user_no_privilege(
    test_client_fixture: starlette.testclient.TestClient, test_rsa_key, setup_new_user
):
    # prepare new IDIR user (with dummy cognito id)
    new_user = setup_new_user(
        TEST_NEW_IDIR_USER.user_type_code,
        TEST_NEW_IDIR_USER.user_name,
        TEST_NEW_IDIR_USER.user_guid,
        TEST_DUMMY_COGNITO_USER_ID,
    )

    claims = jwt_utils.create_jwt_claims()
    # below set "username" is needed so requester can be retrieved from db
    # for the correct new_user
    claims["username"] = new_user.cognito_user_id
    token = jwt_utils.create_jwt_token(test_rsa_key, roles=[], claims=claims)

    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["access"] == []  # empty access expected


def test_get_admin_user_access__user_with_fam_admin_privilege(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    setup_new_user,
    setup_new_app_admin,
    application_repo,
):
    # prepare new IDIR user (with dummy cognito id)
    new_user = setup_new_user(
        TEST_NEW_IDIR_USER.user_type_code,
        TEST_NEW_IDIR_USER.user_name,
        TEST_NEW_IDIR_USER.user_guid,
        TEST_DUMMY_COGNITO_USER_ID,
    )

    claims = jwt_utils.create_jwt_claims()
    claims["username"] = new_user.cognito_user_id
    token = jwt_utils.create_jwt_token(test_rsa_key, roles=[], claims=claims)

    # verify new_user initially does not have any privilege
    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.OK
    result = response.json().get("access")
    assert len(result) == 0

    # assign IDIR new_user for FAM_ADMIN privilege
    setup_new_app_admin(new_user.user_id, TEST_APPLICATION_ID_FAM)

    # verify new_user now contains FAM_ADMIN privilege
    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.OK
    result = response.json().get("access")
    assert len(result) == 1
    access = result[0]
    assert access.get("auth_key") == AdminRoleAuthGroup.FAM_ADMIN  # FAM_ADMIN grants
    grants = access.get("grants")
    fam_app_grant = list(
        filter(lambda x: x["application"]["id"] == TEST_APPLICATION_ID_FAM, grants)
    )[0]
    assert fam_app_grant["application"] is not None
    assert fam_app_grant["application"]["id"] == TEST_APPLICATION_ID_FAM
    assert (
        fam_app_grant["application"]["name"] == TEST_APPLICATION_NAME_FAM
    )  # verify granted app is "FAM", not "FAM_DEV/FAM_TEST"
    assert fam_app_grant["application"]["env"] is None
    assert fam_app_grant["roles"] is None

    other_apps_grant = list(
        filter(lambda x: x["application"]["id"] != TEST_APPLICATION_ID_FAM, grants)
    )
    assert len(other_apps_grant) != 0
    app_1_grant = other_apps_grant[0]
    assert app_1_grant["application"] is not None
    assert app_1_grant["application"]["id"] is not None
    assert app_1_grant["application"]["name"] is not None
    assert app_1_grant["application"]["env"] is not None
    assert app_1_grant["roles"] is None

    fam_applications = application_repo.get_applications()
    db_application_list = list(map(lambda x: x.application_id, fam_applications))
    auth_grant_applications = list(map(lambda x: x["application"]["id"], grants))
    # verify FAM_ADMIN has privilege for granting all apps
    assert len(auth_grant_applications) == len(db_application_list)
    assert set(auth_grant_applications) == set(db_application_list)


def test_get_admin_user_access__user_with_multiple_app_admin_privilege(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    setup_new_user,
    setup_new_app_admin,
    role_repo,
):
    # prepare new IDIR user (with dummy cognito id)
    new_user = setup_new_user(
        TEST_NEW_IDIR_USER.user_type_code,
        TEST_NEW_IDIR_USER.user_name,
        TEST_NEW_IDIR_USER.user_guid,
        TEST_DUMMY_COGNITO_USER_ID,
    )

    # assign IDIR new_user for FOM_DEV and FOM_TEST admin privilege
    setup_new_app_admin(new_user.user_id, TEST_APPLICATION_ID_FOM_DEV)
    setup_new_app_admin(new_user.user_id, TEST_APPLICATION_ID_FOM_TEST)

    claims = jwt_utils.create_jwt_claims()
    claims["username"] = new_user.cognito_user_id
    token = jwt_utils.create_jwt_token(test_rsa_key, roles=[], claims=claims)

    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.OK
    result = response.json().get("access")
    assert len(result) == 1
    access = result[0]
    assert access["auth_key"] == AdminRoleAuthGroup.APP_ADMIN  # APP_ADMIN grants
    grants = access["grants"]
    assert len(grants) == 2  # APP_AdMIN for: FOM_DEV and FOM_TEST
    # FOM DEV grants
    fom_dev_grant = list(
        filter(lambda x: x["application"]["id"] == TEST_APPLICATION_ID_FOM_DEV, grants)
    )[0]
    # FOM DEV grant for "application" the admin can manage
    assert fom_dev_grant["application"]["id"] == TEST_APPLICATION_ID_FOM_DEV
    assert fom_dev_grant["application"]["name"] == TEST_APP_FOM_NAME
    assert fom_dev_grant["application"]["env"] == AppEnv.APP_ENV_TYPE_DEV.value
    # FOM DEV grant for "roles" the admin can manage
    fom_dev_roles_grants = fom_dev_grant["roles"]
    fom_dev_base_roles = role_repo.get_base_roles_by_app_id(TEST_APPLICATION_ID_FOM_DEV)
    assert len(fom_dev_roles_grants) == len(fom_dev_base_roles)
    fom_dev_roles_grants_id_list = list(map(lambda x: x["id"], fom_dev_roles_grants))
    fom_dev_base_role_id_list = list(map(lambda x: x.role_id, fom_dev_base_roles))
    assert set(fom_dev_roles_grants_id_list) == set(fom_dev_base_role_id_list)
    fom_dev_role_grants_reviewer = list(
        filter(lambda x: x["id"] == TEST_FOM_DEV_REVIEWER_ROLE_ID, fom_dev_roles_grants)
    )[0]
    assert fom_dev_role_grants_reviewer["id"] == TEST_FOM_DEV_REVIEWER_ROLE_ID
    assert fom_dev_role_grants_reviewer["name"] == TEST_APP_ROLE_NAME_FOM_REVIEWER
    assert (
        fom_dev_role_grants_reviewer["type_code"] == RoleType.ROLE_TYPE_CONCRETE.value
    )
    fom_dev_roles_grants_submitter = list(
        filter(
            lambda x: x["id"] == TEST_FOM_DEV_SUBMITTER_ROLE_ID, fom_dev_roles_grants
        )
    )[0]
    assert fom_dev_roles_grants_submitter["id"] == TEST_FOM_DEV_SUBMITTER_ROLE_ID
    assert fom_dev_roles_grants_submitter["name"] == TEST_APP_ROLE_NAME_FOM_SUBMITTER
    assert (
        fom_dev_roles_grants_submitter["type_code"] == RoleType.ROLE_TYPE_ABSTRACT.value
    )
    assert fom_dev_roles_grants_submitter["forest_clients"] is None

    # FOM TEST grants
    fom_test_grant = list(
        filter(lambda x: x["application"]["id"] == TEST_APPLICATION_ID_FOM_TEST, grants)
    )[0]
    assert fom_test_grant["application"]["id"] == TEST_APPLICATION_ID_FOM_TEST
    assert fom_test_grant["application"]["name"] == TEST_APP_FOM_NAME
    assert fom_test_grant["application"]["env"] == AppEnv.APP_ENV_TYPE_TEST.value
    fom_test_roles_grants = fom_test_grant["roles"]
    fom_test_base_roles = role_repo.get_base_roles_by_app_id(
        TEST_APPLICATION_ID_FOM_TEST
    )
    assert len(fom_test_roles_grants) == len(fom_test_base_roles)
    fom_test_roles_grants_id_list = list(map(lambda x: x["id"], fom_test_roles_grants))
    fom_test_base_role_id_list = list(map(lambda x: x.role_id, fom_test_base_roles))
    assert set(fom_test_roles_grants_id_list) == set(fom_test_base_role_id_list)
    fom_test_role_grants_reviewer = list(
        filter(
            lambda x: x["id"] == TEST_FOM_TEST_REVIEWER_ROLE_ID, fom_test_roles_grants
        )
    )[0]
    assert fom_test_role_grants_reviewer["id"] == TEST_FOM_TEST_REVIEWER_ROLE_ID
    assert fom_test_role_grants_reviewer["name"] == TEST_APP_ROLE_NAME_FOM_REVIEWER
    assert (
        fom_test_role_grants_reviewer["type_code"] == RoleType.ROLE_TYPE_CONCRETE.value
    )
    fom_test_roles_grants_submitter = list(
        filter(
            lambda x: x["id"] == TEST_FOM_TEST_SUBMITTER_ROLE_ID, fom_test_roles_grants
        )
    )[0]
    assert fom_test_roles_grants_submitter["id"] == TEST_FOM_TEST_SUBMITTER_ROLE_ID
    assert fom_test_roles_grants_submitter["name"] == TEST_APP_ROLE_NAME_FOM_SUBMITTER
    assert (
        fom_test_roles_grants_submitter["type_code"]
        == RoleType.ROLE_TYPE_ABSTRACT.value
    )
    assert fom_dev_roles_grants_submitter["forest_clients"] is None


# test on delegated admin using specific FOM app.
def test_get_admin_user_access__user_with_multiple_delegated_admin_privilege(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    setup_new_user,
    setup_new_fom_delegated_admin,
):
    # prepare new BCEID user (with dummy cognito id)
    new_user = setup_new_user(
        TEST_NEW_BCEID_USER.user_type_code,
        TEST_NEW_BCEID_USER.user_name,
        TEST_NEW_IDIR_USER.user_guid,
        TEST_DUMMY_COGNITO_USER_ID,
    )

    # below assigns new_user multiple delegated admin grants
    # assign new_user FOM_REVIEWER delegated admin to FOM_DEV
    setup_new_fom_delegated_admin(
        new_user.user_id, RoleType.ROLE_TYPE_CONCRETE, AppEnv.APP_ENV_TYPE_DEV
    )
    # assign new_user FOM_SUBMITTER delegated admin role to FOM_TEST
    dga_submitter_forest_clients = [
        TEST_FOREST_CLIENT_NUMBER,
        TEST_FOREST_CLIENT_NUMBER_TWO,
    ]
    setup_new_fom_delegated_admin(
        new_user.user_id,
        RoleType.ROLE_TYPE_ABSTRACT,
        AppEnv.APP_ENV_TYPE_TEST,
        dga_submitter_forest_clients,
    )

    claims = jwt_utils.create_jwt_claims()
    claims["username"] = new_user.cognito_user_id
    token = jwt_utils.create_jwt_token(test_rsa_key, roles=[], claims=claims)

    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.OK
    result = response.json().get("access")
    assert len(result) == 1
    access = result[0]
    assert (
        access["auth_key"] == AdminRoleAuthGroup.DELEGATED_ADMIN
    )  # DELEGATED_ADMIN grants
    grants = access["grants"]
    assert len(grants) == 2  # DELEGATED_ADMIN for: FOM_DEV and FOM_TEST

    # FOM DEV DELEGATED_ADMIN grants
    fom_dev_grant = list(
        filter(lambda x: x["application"]["id"] == TEST_APPLICATION_ID_FOM_DEV, grants)
    )[0]
    # FOM DEV DELEGATED_ADMIN grant for "application" the admin can manage
    assert fom_dev_grant["application"]["id"] == TEST_APPLICATION_ID_FOM_DEV
    assert fom_dev_grant["application"]["name"] == TEST_APP_FOM_NAME
    assert fom_dev_grant["application"]["env"] == AppEnv.APP_ENV_TYPE_DEV.value
    # FOM DEV grant for "role" the admin can manage
    fom_dev_roles_grants = fom_dev_grant["roles"]
    # was setup for ROLE_TYPE_CONCRETE (FOM_REVIEWER), so should only have 1
    assert len(fom_dev_roles_grants) == 1
    fom_dev_role_grants_reviewer = fom_dev_roles_grants[0]
    assert fom_dev_role_grants_reviewer["id"] == TEST_FOM_DEV_REVIEWER_ROLE_ID
    assert fom_dev_role_grants_reviewer["name"] == TEST_APP_ROLE_NAME_FOM_REVIEWER
    assert (
        fom_dev_role_grants_reviewer["type_code"] == RoleType.ROLE_TYPE_CONCRETE.value
    )
    assert fom_dev_role_grants_reviewer["forest_clients"] is None

    # FOM TEST DELEGATED_ADMIN grants
    fom_test_grant = list(
        filter(lambda x: x["application"]["id"] == TEST_APPLICATION_ID_FOM_TEST, grants)
    )[0]
    # FOM DEV DELEGATED_ADMIN grant for "application" the admin can manage
    assert fom_test_grant["application"]["id"] == TEST_APPLICATION_ID_FOM_TEST
    assert fom_test_grant["application"]["name"] == TEST_APP_FOM_NAME
    assert fom_test_grant["application"]["env"] == AppEnv.APP_ENV_TYPE_TEST.value
    # FOM TEST grant for "role" the admin can manage
    fom_test_roles_grants = fom_test_grant["roles"]
    # was setup for ROLE_TYPE_ABSTRACT (FOM_SUBMITTER), so should only have 1
    assert len(fom_dev_roles_grants) == 1
    fom_test_role_grants_submitter = fom_test_roles_grants[0]
    assert fom_test_role_grants_submitter["id"] == TEST_FOM_TEST_SUBMITTER_ROLE_ID
    assert fom_test_role_grants_submitter["name"] == TEST_APP_ROLE_NAME_FOM_SUBMITTER
    assert (
        fom_test_role_grants_submitter["type_code"] == RoleType.ROLE_TYPE_ABSTRACT.value
    )
    # should contains exact 2 forest_clients the new_user can administer
    assert set(fc["forest_client_number"] for fc in fom_test_role_grants_submitter["forest_clients"]) == set(
        dga_submitter_forest_clients
    )


def test_get_admin_user_access__user_with_app_admin_and_delegated_admin_privilege(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    setup_new_user,
    setup_new_app_admin,
    setup_new_fom_delegated_admin,
    role_repo,
):
    # prepare new IDIR user (with dummy cognito id)
    new_user = setup_new_user(
        TEST_NEW_IDIR_USER.user_type_code,
        TEST_NEW_IDIR_USER.user_name,
        TEST_NEW_IDIR_USER.user_guid,
        TEST_DUMMY_COGNITO_USER_ID,
    )

    # assign IDIR new_user for FOM_TEST app admin
    setup_new_app_admin(new_user.user_id, TEST_APPLICATION_ID_FOM_TEST)

    # assign IDIR new_user FOM_REVIEWER delegated admin role to FOM_DEV
    setup_new_fom_delegated_admin(
        new_user.user_id, RoleType.ROLE_TYPE_CONCRETE, AppEnv.APP_ENV_TYPE_DEV
    )
    # assign IDIR new_user FOM_SUBMITTER delegated admin role to FOM_DEV
    dga_submitter_forest_clients = [
        TEST_FOREST_CLIENT_NUMBER,
        TEST_FOREST_CLIENT_NUMBER_TWO,
    ]
    setup_new_fom_delegated_admin(
        new_user.user_id,
        RoleType.ROLE_TYPE_ABSTRACT,
        AppEnv.APP_ENV_TYPE_DEV,
        dga_submitter_forest_clients,
    )

    claims = jwt_utils.create_jwt_claims()
    claims["username"] = new_user.cognito_user_id
    token = jwt_utils.create_jwt_token(test_rsa_key, roles=[], claims=claims)

    response = test_client_fixture.get(
        f"{test_end_point}", headers=jwt_utils.headers(token)
    )
    assert response.status_code == HTTPStatus.OK
    result = response.json().get("access")
    assert len(result) == 2  # contains APP_ADMIN and DELEGATED_ADMIN
    access_app_admin = list(
        filter(lambda x: x["auth_key"] == AdminRoleAuthGroup.APP_ADMIN, result)
    )[0]

    # new_user was granted as FOM_TEST app admin
    app_admin_grants = access_app_admin["grants"]
    assert len(app_admin_grants) == 1
    fom_test_app_admin = app_admin_grants[0]
    assert fom_test_app_admin["application"]["id"] == TEST_APPLICATION_ID_FOM_TEST
    assert fom_test_app_admin["application"]["name"] == TEST_APP_FOM_NAME
    assert fom_test_app_admin["application"]["env"] == AppEnv.APP_ENV_TYPE_TEST.value
    fom_test_roles_grants = fom_test_app_admin["roles"]
    fom_test_base_roles = role_repo.get_base_roles_by_app_id(
        TEST_APPLICATION_ID_FOM_TEST
    )
    assert len(fom_test_roles_grants) == len(fom_test_base_roles)
    fom_test_roles_grants_id_list = list(map(lambda x: x["id"], fom_test_roles_grants))
    fom_test_base_role_id_list = list(map(lambda x: x.role_id, fom_test_base_roles))
    assert set(fom_test_roles_grants_id_list) == set(fom_test_base_role_id_list)
    fom_test_role_grants_reviewer = list(
        filter(
            lambda x: x["id"] == TEST_FOM_TEST_REVIEWER_ROLE_ID, fom_test_roles_grants
        )
    )[0]
    assert fom_test_role_grants_reviewer["id"] == TEST_FOM_TEST_REVIEWER_ROLE_ID
    assert fom_test_role_grants_reviewer["name"] == TEST_APP_ROLE_NAME_FOM_REVIEWER
    assert (
        fom_test_role_grants_reviewer["type_code"] == RoleType.ROLE_TYPE_CONCRETE.value
    )
    assert fom_test_role_grants_reviewer["forest_clients"] is None
    fom_test_roles_grants_submitter = list(
        filter(
            lambda x: x["id"] == TEST_FOM_TEST_SUBMITTER_ROLE_ID, fom_test_roles_grants
        )
    )[0]
    assert fom_test_roles_grants_submitter["id"] == TEST_FOM_TEST_SUBMITTER_ROLE_ID
    assert fom_test_roles_grants_submitter["name"] == TEST_APP_ROLE_NAME_FOM_SUBMITTER
    assert (
        fom_test_roles_grants_submitter["type_code"]
        == RoleType.ROLE_TYPE_ABSTRACT.value
    )
    assert fom_test_roles_grants_submitter["forest_clients"] is None

    # new_user was granted as FOM_DEV delegated admin
    access_delegated_admin = list(
        filter(lambda x: x["auth_key"] == AdminRoleAuthGroup.DELEGATED_ADMIN, result)
    )[0]
    delegated_admin_grants = access_delegated_admin["grants"]
    assert len(delegated_admin_grants) == 1
    # FOM DEV DELEGATED_ADMIN grants
    fom_dev_grant = delegated_admin_grants[0]
    assert fom_dev_grant["application"]["id"] == TEST_APPLICATION_ID_FOM_DEV
    assert fom_dev_grant["application"]["name"] == TEST_APP_FOM_NAME
    assert fom_dev_grant["application"]["env"] == AppEnv.APP_ENV_TYPE_DEV.value
    # FOM DEV grant for "roles" the admin can manage
    fom_dev_roles_grants = fom_dev_grant["roles"]
    # contains two roles the delegated admin can manage
    assert len(fom_dev_roles_grants) == 2
    # reviewer role
    fom_dev_reviewer_grant = list(
        filter(lambda x: x["id"] == TEST_FOM_DEV_REVIEWER_ROLE_ID, fom_dev_roles_grants)
    )[0]
    assert fom_dev_reviewer_grant["id"] == TEST_FOM_DEV_REVIEWER_ROLE_ID
    assert fom_dev_reviewer_grant["name"] == TEST_APP_ROLE_NAME_FOM_REVIEWER
    assert fom_dev_reviewer_grant["type_code"] == RoleType.ROLE_TYPE_CONCRETE.value
    assert fom_dev_reviewer_grant["forest_clients"] is None
    # submitter role
    fom_dev_submitter_grant = list(
        filter(
            lambda x: x["id"] == TEST_FOM_DEV_SUBMITTER_ROLE_ID, fom_dev_roles_grants
        )
    )[0]
    assert fom_dev_submitter_grant["id"] == TEST_FOM_DEV_SUBMITTER_ROLE_ID
    assert fom_dev_submitter_grant["name"] == TEST_APP_ROLE_NAME_FOM_SUBMITTER
    assert fom_dev_submitter_grant["type_code"] == RoleType.ROLE_TYPE_ABSTRACT.value
    assert fom_dev_submitter_grant["forest_clients"] is not None
    assert set(fc["forest_client_number"] for fc in fom_dev_submitter_grant["forest_clients"]) == set(
        dga_submitter_forest_clients
    )