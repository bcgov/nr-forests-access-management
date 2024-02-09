import logging
from http import HTTPStatus

import starlette.testclient
import tests.jwt_utils as jwt_utils
from api.app.constants import AdminRoleAuthGroup
from api.app.main import apiPrefix
from tests.constants import (TEST_APPLICATION_ID_FAM,
                             TEST_APPLICATION_NAME_FAM,
                             TEST_DUMMY_COGNITO_USER_ID, TEST_NEW_IDIR_USER)

LOGGER = logging.getLogger(__name__)
test_end_point = f"{apiPrefix}/admin-user-accesses"

# Below tests are based on endpoint json sample output at confluence design:
# https://apps.nrs.gov.bc.ca/int/confluence/display/FSAST1/Delegated+Access+Administration+Design


def test_get_admin_user_access__user_no_privilege(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    setup_new_user
):
    # prepare new IDIR user (with dummy cognito id)
    new_user = setup_new_user(TEST_NEW_IDIR_USER.user_type_code,
                              TEST_NEW_IDIR_USER.user_name,
                              TEST_DUMMY_COGNITO_USER_ID)

    claims = jwt_utils.create_jwt_claims()
    # below set "username" is needed so requester can be retrieved from db
    # for the correct new_user
    claims["username"] = new_user.cognito_user_id
    token = jwt_utils.create_jwt_token(test_rsa_key, roles=[], claims=claims)

    response = test_client_fixture.get(
       f"{test_end_point}", headers=jwt_utils.headers(token))
    assert response.status_code == HTTPStatus.OK
    assert response.json()['access'] == []  # empty access expected


def test_get_admin_user_access__user_with_FAM_ADMIN_privilege(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    setup_new_user,
    setup_new_app_admin,
    application_repo
):
    # prepare new IDIR user (with dummy cognito id)
    new_user = setup_new_user(TEST_NEW_IDIR_USER.user_type_code,
                              TEST_NEW_IDIR_USER.user_name,
                              TEST_DUMMY_COGNITO_USER_ID)
    # assign new_user for FAM_ADMIN
    setup_new_app_admin(new_user.user_id, TEST_APPLICATION_ID_FAM)

    claims = jwt_utils.create_jwt_claims()
    claims["username"] = new_user.cognito_user_id
    token = jwt_utils.create_jwt_token(test_rsa_key, roles=[], claims=claims)

    response = test_client_fixture.get(
       f"{test_end_point}", headers=jwt_utils.headers(token))
    assert response.status_code == HTTPStatus.OK
    result = response.json().get("access")
    assert len(result) == 1
    access = result[0]
    assert access.get("auth_key") == AdminRoleAuthGroup.FAM_ADMIN  # FAM_ADMIN grants
    grants = access.get("grants")
    fam_app_grant = list(filter(lambda x: x["application"]["id"] == TEST_APPLICATION_ID_FAM, grants))[0]
    assert fam_app_grant["application"] is not None
    assert fam_app_grant["application"]["id"] == TEST_APPLICATION_ID_FAM
    assert fam_app_grant["application"]["name"] == TEST_APPLICATION_NAME_FAM  # verify grante app is "FAM", not "FAM_DEV/FAM_TEST"
    assert fam_app_grant["application"]["env"] is None
    assert fam_app_grant["roles"] is None

    other_apps_grant = list(filter(lambda x: x["application"]["id"] != TEST_APPLICATION_ID_FAM, grants))
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




    # LOGGER.info(f"access~~: {response.json()}")
# user with FAM_ADMIN privilege
# user with multiple APP_ADMIN
# user with delegated admin
# user with APP_ADMIN and delegated admin