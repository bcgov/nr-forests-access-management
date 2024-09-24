import copy
import logging
from http import HTTPStatus

import starlette.testclient
import testspg.db_test_utils as db_test_utils
import testspg.jwt_utils as jwt_utils
from api.app.constants import (ERROR_CODE_DIFFERENT_ORG_GRANT_PROHIBITED,
                               ERROR_CODE_SELF_GRANT_PROHIBITED,
                               ERROR_CODE_TERMS_CONDITIONS_REQUIRED, UserType)
from api.app.crud import crud_application, crud_role, crud_user, crud_user_role
from api.app.crud.services.permission_audit_service import \
    PermissionAuditService
from api.app.jwt_validation import ERROR_PERMISSION_REQUIRED
from api.app.main import apiPrefix
from api.app.models.model import FamPrivilegeChangeAudit, FamUser
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from testspg.conftest import create_test_user_role_assignment
from testspg.constants import (ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID,
                               ACCESS_GRANT_FOM_DEV_AR_00000001_IDIR,
                               ACCESS_GRANT_FOM_DEV_AR_00001018_BCEID_L3T,
                               ACCESS_GRANT_FOM_DEV_AR_00001018_IDIR,
                               ACCESS_GRANT_FOM_DEV_CR_BCEID_L3T,
                               ACCESS_GRANT_FOM_DEV_CR_BCEID_L4T,
                               ACCESS_GRANT_FOM_DEV_CR_IDIR,
                               ACCESS_GRANT_FOM_TEST_CR_IDIR,
                               BUSINESS_GUID_BCEID_LOAD_3_TEST,
                               BUSINESS_GUID_BCEID_LOAD_4_TEST,
                               FC_NUMBER_EXISTS_ACTIVE_00001011,
                               FC_NUMBER_EXISTS_DEACTIVATED,
                               FC_NUMBER_NOT_EXISTS, FOM_DEV_APPLICATION_ID,
                               FOM_DEV_REVIEWER_ROLE_ID,
                               FOM_DEV_SUBMITTER_ROLE_ID,
                               FOM_TEST_APPLICATION_ID)

LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/user_role_assignment"

ERROR_DUPLICATE_USER_ROLE = "already assigned to user"


# ------------------ test create user role assignment ----------------------- #


def test_create_user_role_assignment_many_not_authorized(
    test_client_fixture: starlette.testclient.TestClient, test_rsa_key
):
    """
    test user has no authentication to the app
    user without FOM_DEV_ADMIN role and not delegated admin of FOM DEV cannot grant FOM_DEV roles
    """
    token = jwt_utils.create_jwt_token(test_rsa_key)
    response = test_client_fixture.post(
        f"{endPoint}",
        json=ACCESS_GRANT_FOM_DEV_CR_IDIR,
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    data = response.json()
    assert data["detail"]["code"] == ERROR_PERMISSION_REQUIRED
    assert (
        data["detail"]["description"]
        == "Requester has no admin or delegated admin access to the application."
    )



def test_create_user_role_assignment_many_with_concrete_role_authorize_by_delegated_admin(
    db_pg_session: Session,
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    override_get_verified_target_user,
    override_enforce_bceid_terms_conditions_guard,
    mocker
):
    """
    test if user is not app admin, but is delegated admin with the correct privilege, will be able to grant access

    this test case uses business bceid user with FOM DEV FOM_REVIEWER privilege as example
    test if business bceid user is delegated admin of FOM DEV for FOM_REVIEWER role,
    able to grant FOM_REVIEWER access to a business bceid user from same org
    """
    # override router guard dependencies
    override_enforce_bceid_terms_conditions_guard()
    override_get_verified_target_user(
        {
            **ACCESS_GRANT_FOM_DEV_CR_BCEID_L3T,
            "business_guid": BUSINESS_GUID_BCEID_LOAD_3_TEST,
        }
    )
    store_user_permissions_granted_audit_history_fn_spy = mocker.spy(PermissionAuditService, 'store_user_permissions_granted_audit_history')

    # create a token for business bceid user COGNITO_USERNAME_BCEID with no app admin role,
    # this user has delegated admin privilege which is granted in the local sql
    token = jwt_utils.create_jwt_token(
        test_rsa_key, [], jwt_utils.COGNITO_USERNAME_BCEID_DELEGATED_ADMIN
    )
    response = test_client_fixture.post(
        f"{endPoint}",
        json=ACCESS_GRANT_FOM_DEV_CR_BCEID_L3T,
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() is not None
    data = response.json().get("assignments_detail")
    assert len(data) == 1
    assert data[0].get("status_code") == HTTPStatus.OK
    detail = data[0].get("detail")
    assert "user_role_xref_id" in detail
    assert "user_id" in detail
    assert "role_id" in detail
    assert "application_id" in detail.get("role").get("application")

    # verify audit record created (service being called only)
    # for detail tests see test_permission_audit_service.py).
    performer = db_pg_session.query(FamUser).filter(
        FamUser.cognito_user_id == jwt_utils.COGNITO_USERNAME_BCEID_DELEGATED_ADMIN
    ).one()
    audit_record = db_pg_session.query(FamPrivilegeChangeAudit).filter(
		FamPrivilegeChangeAudit.application_id == detail["role"]["application"]["application_id"],
		FamPrivilegeChangeAudit.change_performer_user_id == performer.user_id,
		FamPrivilegeChangeAudit.change_target_user_id == detail["user_id"]
	).one_or_none()
    assert store_user_permissions_granted_audit_history_fn_spy.call_count == 1
    assert audit_record is not None


def test_create_user_role_assignment_many_with_abstract_role_authorize_by_delegated_admin(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    override_get_verified_target_user,
    override_enforce_bceid_terms_conditions_guard,
):
    """
    test if user is not app admin, but is delegated admin with the correct privilege, will be able to grant access

    this test case uses business bceid user with FOM DEV FOM_SUBMITTER_00001018 privilege as example
    test if business bceid user is delegated admin of FOM DEV for FOM_SUBMITTER role with forest client number 00001018,
    able to grant FOM_SUBMITTER_00001018 access for business bceid user from same org,
    will not be able to grant access with other forest client numbers like FOM_SUBMITTER_00001011
    """
    # override router guard dependencies
    override_enforce_bceid_terms_conditions_guard()
    override_get_verified_target_user(
        {
            **ACCESS_GRANT_FOM_DEV_AR_00001018_BCEID_L3T,
            "business_guid": BUSINESS_GUID_BCEID_LOAD_3_TEST,
        }
    )

    # create a token for business bceid user COGNITO_USERNAME_BCEID with no app admin role,
    # this user has delegated admin privilege which is granted in the local sql
    token = jwt_utils.create_jwt_token(
        test_rsa_key, [], jwt_utils.COGNITO_USERNAME_BCEID_DELEGATED_ADMIN
    )
    response = test_client_fixture.post(
        f"{endPoint}",
        json=ACCESS_GRANT_FOM_DEV_AR_00001018_BCEID_L3T,
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() is not None
    data = response.json().get("assignments_detail")
    assert len(data) == 1
    assert data[0].get("status_code") == HTTPStatus.OK
    detail = data[0].get("detail")
    assert "user_role_xref_id" in detail
    assert "user_id" in detail
    assert "role_id" in detail
    assert "application_id" in detail.get("role").get("application")

    response = test_client_fixture.post(
        f"{endPoint}",
        json={
            **ACCESS_GRANT_FOM_DEV_AR_00001018_BCEID_L3T,
            "forest_client_numbers": [FC_NUMBER_EXISTS_ACTIVE_00001011],
        },
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    data = response.json()
    # business bceid user has no privilege to grant FOM_SUBMITTER access with forest client number 00001011
    assert data["detail"]["code"] == ERROR_PERMISSION_REQUIRED
    assert (
        data["detail"]["description"]
        == "Requester has no privilege to grant this access."
    )


def test_create_user_role_assignment_many_bceid_cannot_grant_idir_access(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    override_get_verified_target_user,
    override_enforce_bceid_terms_conditions_guard,
):
    """
    test business bceid user cannnot grant idir user access
    """
    # override router guard dependencies
    override_enforce_bceid_terms_conditions_guard()
    override_get_verified_target_user()

    # create a token for business bceid user COGNITO_USERNAME_BCEID with no app admin role,
    # this user has delegated admin privilege which is granted in the local sql
    token = jwt_utils.create_jwt_token(
        test_rsa_key,
        roles=[],
        username=jwt_utils.COGNITO_USERNAME_BCEID_DELEGATED_ADMIN,
    )
    response = test_client_fixture.post(
        f"{endPoint}",
        json=ACCESS_GRANT_FOM_DEV_CR_IDIR,
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    data = response.json()
    # business bceid user cannot grant idir user access
    assert data["detail"]["code"] == ERROR_PERMISSION_REQUIRED
    assert (
        data["detail"]["description"]
        == "Business BCEID requester has no privilege to grant this access to IDIR user."
    )


def test_create_user_role_assignment_many_bceid_cannot_grant_access_from_diff_org(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    override_get_verified_target_user,
    override_enforce_bceid_terms_conditions_guard,
):
    """
    test business bceid user cannnot grant business bceid user access from different organization
    """
    # override router guard dependencies
    override_enforce_bceid_terms_conditions_guard()
    override_get_verified_target_user(
        {
            **ACCESS_GRANT_FOM_DEV_CR_BCEID_L4T,
            "business_guid": BUSINESS_GUID_BCEID_LOAD_4_TEST,
        }
    )

    # create a token for business bceid user COGNITO_USERNAME_BCEID with no app admin role,
    # this user has delegated admin privilege which is granted in the local sql
    token = jwt_utils.create_jwt_token(
        test_rsa_key,
        roles=[],
        username=jwt_utils.COGNITO_USERNAME_BCEID_DELEGATED_ADMIN,
    )
    response = test_client_fixture.post(
        f"{endPoint}",
        json=ACCESS_GRANT_FOM_DEV_CR_BCEID_L4T,  # Business bceid user LOAD-4-TEST is already created in local_sql with business_guid,
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    data = response.json()
    # business bceid user cannot grant business bceid user access from different organization
    assert data["detail"]["code"] == ERROR_CODE_DIFFERENT_ORG_GRANT_PROHIBITED
    assert (
        data["detail"]["description"]
        == "Managing for different organization is not allowed."
    )


def test_create_user_role_assignment_many_with_concrete_role(
    test_client_fixture: starlette.testclient.TestClient,
    db_pg_session: Session,
    fom_dev_access_admin_token,
    get_current_requester_by_token,
    override_get_verified_target_user,
):
    """
    test assign a concrete role to a user
    """
    # override router guard dependencies
    override_get_verified_target_user()

    response = test_client_fixture.post(
        f"{endPoint}",
        json=ACCESS_GRANT_FOM_DEV_CR_IDIR,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() is not None
    data = response.json().get("assignments_detail")
    assert len(data) == 1
    assert data[0].get("status_code") == HTTPStatus.OK
    detail = data[0].get("detail")
    assert "user_role_xref_id" in detail
    assert "user_id" in detail
    assert "role_id" in detail
    assert "application_id" in detail.get("role").get("application")

    # verify assignment did get created
    # retrieved requester for current request.
    requester = get_current_requester_by_token(fom_dev_access_admin_token)
    assignment_user_role_concrete = crud_application.get_application_role_assignments(
        db=db_pg_session,
        application_id=detail["role"]["application"]["application_id"],
        requester=requester
    )
    assert len(assignment_user_role_concrete) == 1
    assert (
        assignment_user_role_concrete[0].user_role_xref_id
        == detail["user_role_xref_id"]
    )

    # verify assignment linking to correct user
    assignment_user = crud_user.get_user(
        db_pg_session, assignment_user_role_concrete[0].user_id
    )
    assert assignment_user is not None

    # verify assignment linking to correct role and parent role
    assignment_role = crud_role.get_role(
        db_pg_session, assignment_user_role_concrete[0].role_id
    )
    assert assignment_role is not None
    assert assignment_role.parent_role_id is None

    # cleanup
    response = test_client_fixture.delete(
        f"{endPoint}/{detail['user_role_xref_id']}",
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_create_user_role_assignment_many_with_concrete_role_duplicate(
    test_client_fixture: starlette.testclient.TestClient,
    fom_dev_access_admin_token,
    override_get_verified_target_user,
):
    """
    test assign same role for the same user
    """
    # override router guard dependencies
    override_get_verified_target_user()

    # create user role assignment the first time
    response = test_client_fixture.post(
        f"{endPoint}",
        json=ACCESS_GRANT_FOM_DEV_CR_IDIR,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.OK

    # create user role assignment the second time
    response = test_client_fixture.post(
        f"{endPoint}",
        json=ACCESS_GRANT_FOM_DEV_CR_IDIR,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json().get("assignments_detail")
    assert len(data) == 1
    assert data[0].get("status_code") == HTTPStatus.CONFLICT
    assert data[0].get("error_message").find(ERROR_DUPLICATE_USER_ROLE) != -1

    # cleanup
    response = test_client_fixture.delete(
        f"{endPoint}/{data[0]['detail']['user_role_xref_id']}",
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_create_user_role_assignment_many_with_abstract_role_without_forestclient(
    test_client_fixture: starlette.testclient.TestClient,
    fom_dev_access_admin_token,
    override_get_verified_target_user,
):
    """
    test assign an abscrate role to a user without forest client number
    """
    # override router guard dependencies
    override_get_verified_target_user(ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID)

    COPY_TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT = copy.deepcopy(
        ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID
    )
    COPY_TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT.pop("forest_client_numbers")
    response = test_client_fixture.post(
        f"{endPoint}",
        json=COPY_TEST_USER_ROLE_ASSIGNMENT_FOM_DEV_ABSTRACT,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == 400
    assert (
        response.json()["detail"].get("description")
        == "Invalid user role assignment request, missing forest client number."
    )


def test_create_user_role_assignment_many_with_abstract_role(
    test_client_fixture: starlette.testclient.TestClient,
    db_pg_session: Session,
    fom_dev_access_admin_token,
    get_current_requester_by_token,
    override_get_verified_target_user,
):
    """
    test assign an abscrate role to a user with multiple forest client numbers
    """
    # override router guard dependencies
    override_get_verified_target_user(ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID)

    response = test_client_fixture.post(
        f"{endPoint}",
        json={
            **ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID,
            "forest_client_numbers": ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID[
                "forest_client_numbers"
            ]
            + [FC_NUMBER_EXISTS_ACTIVE_00001011],
        },
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() is not None
    data = response.json().get("assignments_detail")
    assert len(data) == 2
    assert data[0].get("status_code") == HTTPStatus.OK
    assert data[1].get("status_code") == HTTPStatus.OK

    # verify assignment did get created
    # retrieved requester for current request.
    requester = get_current_requester_by_token(fom_dev_access_admin_token)
    assignment_user_role_abstract = crud_application.get_application_role_assignments(
        db=db_pg_session,
        application_id=data[0]["detail"]["role"]["application"]["application_id"],
        requester=requester,
    )
    assert len(assignment_user_role_abstract) == 2
    assert assignment_user_role_abstract[0].user_role_xref_id in [
        data[0]["detail"]["user_role_xref_id"],
        data[1]["detail"]["user_role_xref_id"],
    ]
    assert assignment_user_role_abstract[1].user_role_xref_id in [
        data[0]["detail"]["user_role_xref_id"],
        data[1]["detail"]["user_role_xref_id"],
    ]
    # verify assignment linking to correct user
    assignment_user = crud_user.get_user(
        db_pg_session, assignment_user_role_abstract[0].user_id
    )
    assert assignment_user is not None
    # verify assignment linking to correct role and parent role
    assignment_role = crud_role.get_role(
        db_pg_session, assignment_user_role_abstract[0].role_id
    )
    assert assignment_role is not None
    assert assignment_role.parent_role_id == FOM_DEV_SUBMITTER_ROLE_ID

    # cleanup
    response = test_client_fixture.delete(
        f"{endPoint}/{data[0]['detail']['user_role_xref_id']}",
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.NO_CONTENT
    response = test_client_fixture.delete(
        f"{endPoint}/{data[1]['detail']['user_role_xref_id']}",
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_create_user_role_assignment_many_with_same_username(
    test_client_fixture: starlette.testclient.TestClient,
    db_pg_session: Session,
    fom_dev_access_admin_token,
    get_current_requester_by_token,
    override_get_verified_target_user,
):
    # override router guard dependencies
    override_get_verified_target_user()

    # create a user role assignment
    response = test_client_fixture.post(
        f"{endPoint}",
        json=ACCESS_GRANT_FOM_DEV_CR_IDIR,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.OK
    assignment_one = response.json().get("assignments_detail")[0]["detail"]

    # allow create a user role assignment with the same username, different role
    response = test_client_fixture.post(
        f"{endPoint}",
        json=ACCESS_GRANT_FOM_DEV_AR_00000001_IDIR,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.OK
    assignment_two = response.json().get("assignments_detail")[0]["detail"]

    # allow create a user role assignment with the same username, different role
    response = test_client_fixture.post(
        f"{endPoint}",
        json=ACCESS_GRANT_FOM_DEV_AR_00001018_IDIR,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.OK
    assignment_three = response.json().get("assignments_detail")[0]["detail"]

    # retrieved requester for current request.
    requester = get_current_requester_by_token(fom_dev_access_admin_token)
    assignment_user_role_items = crud_application.get_application_role_assignments(
        db=db_pg_session,
        application_id=assignment_one["role"]["application"]["application_id"],
        requester=requester,
    )
    assert len(assignment_user_role_items) == 3

    # cleanup
    response = test_client_fixture.delete(
        f"{endPoint}/{assignment_one['user_role_xref_id']}",
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.NO_CONTENT

    response = test_client_fixture.delete(
        f"{endPoint}/{assignment_two['user_role_xref_id']}",
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.NO_CONTENT

    response = test_client_fixture.delete(
        f"{endPoint}/{assignment_three['user_role_xref_id']}",
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_assign_same_application_roles_for_different_environments(
    test_client_fixture: starlette.testclient.TestClient,
    db_pg_session: Session,
    fom_dev_access_admin_token,
    fom_test_access_admin_token,
    get_current_requester_by_token,
    override_get_verified_target_user,
):
    # override router guard dependencies
    override_get_verified_target_user()

    # create a user role assignment
    response = test_client_fixture.post(
        f"{endPoint}",
        json=ACCESS_GRANT_FOM_DEV_CR_IDIR,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.OK
    fom_dev_user_role_assignment = response.json().get("assignments_detail")[0]["detail"]
    assert "user_role_xref_id" in fom_dev_user_role_assignment

    # create a user role assignment with same username and type, but for FOM_TEST role
    response = test_client_fixture.post(
        f"{endPoint}",
        json=ACCESS_GRANT_FOM_TEST_CR_IDIR,
        headers=jwt_utils.headers(fom_test_access_admin_token),
    )
    assert response.status_code == HTTPStatus.OK
    fom_test_user_role_assignment = response.json().get("assignments_detail")[0]["detail"]
    assert "user_role_xref_id" in fom_test_user_role_assignment

    # verify assignment id not the same
    assignment_user_role_id_dev = fom_dev_user_role_assignment["user_role_xref_id"]
    assignment_user_role_id_test = fom_test_user_role_assignment["user_role_xref_id"]
    assert assignment_user_role_id_dev != assignment_user_role_id_test

    # verify role id not the same
    assignment_role_id_dev = fom_dev_user_role_assignment["role_id"]
    assignment_role_id_test = fom_test_user_role_assignment["role_id"]
    assert assignment_role_id_dev != assignment_role_id_test

    # verify application id
    assert fom_dev_user_role_assignment["role"]["application"]["application_id"] == FOM_DEV_APPLICATION_ID
    assert fom_test_user_role_assignment["role"]["application"]["application_id"] == FOM_TEST_APPLICATION_ID

    # verify assignment did get created for fom_dev
    # retrieved requester for current request.
    fom_dev_access_admin_requester = get_current_requester_by_token(
        fom_dev_access_admin_token
    )
    assignment_user_role_items = crud_application.get_application_role_assignments(
        db=db_pg_session,
        application_id=FOM_DEV_APPLICATION_ID,
        requester=fom_dev_access_admin_requester,
    )
    assert len(assignment_user_role_items) == 1
    assert (
        assignment_user_role_items[0].user_role_xref_id
        == fom_dev_user_role_assignment["user_role_xref_id"]
    )

    # verify assignment did get created for fom_test
    # retrieved requester for current request.
    fom_test_access_admin_requester = get_current_requester_by_token(
        fom_test_access_admin_token
    )
    assignment_user_role_items = crud_application.get_application_role_assignments(
        db=db_pg_session,
        application_id=FOM_TEST_APPLICATION_ID,
        requester=fom_test_access_admin_requester,
    )
    assert len(assignment_user_role_items) == 1
    assert (
        assignment_user_role_items[0].user_role_xref_id
        == fom_test_user_role_assignment["user_role_xref_id"]
    )

    # cleanup
    response = test_client_fixture.delete(
        f"{endPoint}/{fom_dev_user_role_assignment['user_role_xref_id']}",
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.NO_CONTENT

    # verify no user role assignment for fom_dev, but still have one for fom_test
    assignment_user_role_items = crud_application.get_application_role_assignments(
        db=db_pg_session,
        application_id=FOM_DEV_APPLICATION_ID,
        requester=fom_dev_access_admin_requester,
    )
    assert len(assignment_user_role_items) == 0
    assignment_user_role_items = crud_application.get_application_role_assignments(
        db=db_pg_session,
        application_id=FOM_TEST_APPLICATION_ID,
        requester=fom_test_access_admin_requester,
    )
    assert len(assignment_user_role_items) == 1

    # cleanup
    response = test_client_fixture.delete(
        f"{endPoint}/{fom_test_user_role_assignment['user_role_xref_id']}",
        headers=jwt_utils.headers(fom_test_access_admin_token),
    )
    assert response.status_code == HTTPStatus.NO_CONTENT

    # verify no user role assignment for fom_test
    assignment_user_role_items = crud_application.get_application_role_assignments(
        db=db_pg_session,
        application_id=FOM_TEST_APPLICATION_ID,
        requester=fom_test_access_admin_requester,
    )
    assert len(assignment_user_role_items) == 0


def test_user_role_forest_client_number_not_exist_bad_request(
    test_client_fixture: TestClient,
    fom_dev_access_admin_token,
    override_get_verified_target_user,
):
    """
    Test assign user role with none-existing forest client number should be
    rejected.
    """
    # override router guard dependencies
    override_get_verified_target_user(ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID)

    client_number_not_exists = FC_NUMBER_NOT_EXISTS
    invalid_request = {
        **ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID,
        "forest_client_numbers": [client_number_not_exists],
    }
    response = test_client_fixture.post(
        f"{endPoint}",
        json=invalid_request,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() is not None
    assert (
        f"Forest Client Number {client_number_not_exists} does not exist."
        in response.json()["detail"].get("description")
    )


def test_user_role_forest_client_number_inactive_bad_request(
    test_client_fixture: TestClient,
    fom_dev_access_admin_token,
    override_get_verified_target_user,
):
    """
    Test assign user role with inactive forest client number should be
    rejected.
    """
    # override router guard dependencies
    override_get_verified_target_user(ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID)
    invalid_request = {
        **ACCESS_GRANT_FOM_DEV_AR_00000001_BCEID,
        "forest_client_numbers": [
            FC_NUMBER_EXISTS_ACTIVE_00001011,
            FC_NUMBER_EXISTS_DEACTIVATED,
        ],
    }
    response = test_client_fixture.post(
        f"{endPoint}",
        json=invalid_request,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() is not None
    assert (
        f"Forest client number {FC_NUMBER_EXISTS_DEACTIVATED} is not in active status"
        in response.json()["detail"].get("description")
    )


def test_self_grant_fail(
    test_client_fixture: starlette.testclient.TestClient,
    fom_dev_access_admin_token,
    db_pg_session: Session,
    override_get_verified_target_user,
):
    # Setup challenge: The user in the json sent to the service must match the user
    # in the JWT security token.
    user_role_assignment_request_data = {
        "user_name": jwt_utils.IDIR_USERNAME,
        "user_type_code": UserType.IDIR,
        "role_id": FOM_DEV_REVIEWER_ROLE_ID,
        "user_guid": jwt_utils.IDP_USER_GUID,
    }

    # override router guard dependencies
    override_get_verified_target_user(user_role_assignment_request_data)

    response = test_client_fixture.post(
        f"{endPoint}",
        json=user_role_assignment_request_data,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )

    row = db_test_utils.get_user_role_by_cognito_user_id_and_role_id(
        db_pg_session, jwt_utils.COGNITO_USERNAME, FOM_DEV_REVIEWER_ROLE_ID
    )
    assert row is None, "Expected user role assignment not to be created"

    jwt_utils.assert_error_response(response, 403, ERROR_CODE_SELF_GRANT_PROHIBITED)


def test_create_user_role_assignment_many_new_bceid_user_save_business_guid(
    test_client_fixture: starlette.testclient.TestClient,
    db_pg_session: Session,
    override_get_verified_target_user,
    fom_dev_access_admin_token,
):
    ACCESS_GRANT_FOM_DEV_CR_BCEID_NEW_USER = {
        "user_name": "TESTUSER_NOTIN_DB",
        "user_guid": "somerandomguid23AE535428F171BF13",
        "user_type_code": UserType.BCEID,
        "role_id": FOM_DEV_REVIEWER_ROLE_ID,
    }

    # override router guard dependencies
    override_get_verified_target_user(ACCESS_GRANT_FOM_DEV_CR_BCEID_NEW_USER)

    # verify user does not exist before creation.
    user = crud_user.get_user_by_domain_and_name(
        db=db_pg_session,
        user_name=ACCESS_GRANT_FOM_DEV_CR_BCEID_NEW_USER["user_name"],
        user_type_code=ACCESS_GRANT_FOM_DEV_CR_BCEID_NEW_USER["user_type_code"],
    )
    assert user is None

    # override router guard dependencies
    mocked_data = {
        **ACCESS_GRANT_FOM_DEV_CR_BCEID_NEW_USER,
        "business_guid": "mockedbusinessguid5D4ACA9FA901EE",
    }
    # override it for test to avoid calling external idim-proxy
    override_get_verified_target_user(mocked_data)

    # create BCeID user/role assignment. Expecting it will save business_guid
    # from mocked_data.business_guid
    response = test_client_fixture.post(
        f"{endPoint}",
        json=ACCESS_GRANT_FOM_DEV_CR_BCEID_NEW_USER,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.OK

    # new user created
    user = crud_user.get_user_by_domain_and_name(
        db=db_pg_session,
        user_name=ACCESS_GRANT_FOM_DEV_CR_BCEID_NEW_USER["user_name"],
        user_type_code=ACCESS_GRANT_FOM_DEV_CR_BCEID_NEW_USER["user_type_code"],
    )
    assert user is not None
    # verify business_guid is saved to the user.
    assert user.business_guid == mocked_data["business_guid"]


# ---------------- Test delete user role assignment ------------ #


def test_delete_user_role_assignment_not_authorized(
    test_client_fixture: starlette.testclient.TestClient,
    fom_dev_access_admin_token,
    test_rsa_key,
    override_get_verified_target_user,
):
    """
    test if user is not app admin, and not app delegated admin, can not remove user role assginments of the application

    this test case uses FOM DEV as example
    test if user is not app admin and not delegated admin of FOM DEV, cannot remove FOM DEV user role assginments
    """
    # override router guard dependencies
    override_get_verified_target_user()

    # create a user role assignment
    user_role_xref_id = create_test_user_role_assignment(
        test_client_fixture,
        fom_dev_access_admin_token,
        ACCESS_GRANT_FOM_DEV_CR_IDIR,
    )

    # create a token for idir user without any app admin roles and no delegated admin privilege
    token = jwt_utils.create_jwt_token(test_rsa_key, roles=[])
    response = test_client_fixture.delete(
        f"{endPoint}/{user_role_xref_id}",
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    data = response.json()
    assert data["detail"]["code"] == ERROR_PERMISSION_REQUIRED
    assert (
        data["detail"]["description"]
        == "Requester has no admin or delegated admin access to the application."
    )


def test_delete_user_role_assignment_authorize_by_delegated_admin(
    test_client_fixture: starlette.testclient.TestClient,
    fom_dev_access_admin_token,
    test_rsa_key,
    override_get_verified_target_user,
    override_enforce_bceid_terms_conditions_guard,
):
    """
    test if user is not app admin, but is delegated admin with the correct privilege, will be able to remove access

    this test case uses business bceid user with FOM DEV FOM_REVIEWER privilege as example
    test if business bceid user is delegated admin of FOM DEV for FOM_REVIEWER role,
    able to remove FOM_REVIEWER access for business bceid user from same org
    """
    # override router guard dependencies
    override_enforce_bceid_terms_conditions_guard()
    override_get_verified_target_user(
        {
            **ACCESS_GRANT_FOM_DEV_CR_BCEID_L3T,
            "business_guid": BUSINESS_GUID_BCEID_LOAD_3_TEST,
        }
    )

    # create a user role assignment for a business bceid user within the same organization as the user COGNITO_USERNAME_BCEID
    user_role_xref_id = create_test_user_role_assignment(
        test_client_fixture,
        fom_dev_access_admin_token,
        ACCESS_GRANT_FOM_DEV_CR_BCEID_L3T,
    )

    # create a token for business bceid user COGNITO_USERNAME_BCEID without any app admin role,
    # this user has delegated admin privilege which is granted in the local sql
    token = jwt_utils.create_jwt_token(
        test_rsa_key,
        roles=[],
        username=jwt_utils.COGNITO_USERNAME_BCEID_DELEGATED_ADMIN,
    )
    response = test_client_fixture.delete(
        f"{endPoint}/{user_role_xref_id}",
        headers=jwt_utils.headers(token),
    )
    # delete is successful
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_user_role_assignment_with_forest_client_number(
    test_client_fixture: starlette.testclient.TestClient,
    fom_dev_access_admin_token,
    test_rsa_key,
    override_get_verified_target_user,
    override_enforce_bceid_terms_conditions_guard,
    mocker
):
    """
    test if user is not app admin, but is delegated admin with the correct privilege, will be able to remove access

    this test case uses business bceid user with FOM DEV FOM_SUBMITTER_00001018 privilege as example
    test if business bceid user is delegated admin of FOM DEV for FOM_SUBMITTER role with forest client number 00001018,
    able to remove FOM_SUBMITTER_00001018 access for business bceid user from same org,
    will not be able to remove access with other forest client numbers like FOM_SUBMITTER_00001011
    """
    # override router guard dependencies
    override_enforce_bceid_terms_conditions_guard()
    override_get_verified_target_user(
        {
            **ACCESS_GRANT_FOM_DEV_AR_00001018_BCEID_L3T,
            "business_guid": BUSINESS_GUID_BCEID_LOAD_3_TEST,
        }
    )

    # create a user role assignment for a business bceid user within the same organization as the user COGNITO_USERNAME_BCEID
    # with abstract role FOM_SUBMITTER and forest client number 00001018
    user_role_xref_id = create_test_user_role_assignment(
        test_client_fixture,
        fom_dev_access_admin_token,
        ACCESS_GRANT_FOM_DEV_AR_00001018_BCEID_L3T,
    )

    store_user_permissions_revoked_audit_history_fn_spy = mocker.spy(PermissionAuditService, 'store_user_permissions_revoked_audit_history')

    # create a token for business bceid user COGNITO_USERNAME_BCEID with no app admin role,
    # this user has delegated admin privilege which is granted in the local sql
    token = jwt_utils.create_jwt_token(
        test_rsa_key, [], jwt_utils.COGNITO_USERNAME_BCEID_DELEGATED_ADMIN
    )
    response = test_client_fixture.delete(
        f"{endPoint}/{user_role_xref_id}",
        headers=jwt_utils.headers(token),
    )
    # delete is successful
    assert response.status_code == HTTPStatus.NO_CONTENT

    # verify audit record action (service being called only)
    # for detail tests see test_permission_audit_service.py).
    assert store_user_permissions_revoked_audit_history_fn_spy.call_count == 1

    # create a user role assignment for a business bceid user within the same organization as the user COGNITO_USERNAME_BCEID
    # with abstract role FOM_SUBMITTER and forest client number 00001011
    user_role_xref_id = create_test_user_role_assignment(
        test_client_fixture,
        fom_dev_access_admin_token,
        {
            **ACCESS_GRANT_FOM_DEV_AR_00001018_BCEID_L3T,
            "forest_client_numbers": [FC_NUMBER_EXISTS_ACTIVE_00001011],
        },
    )
    response = test_client_fixture.delete(
        f"{endPoint}/{user_role_xref_id}",
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    data = response.json()
    # business bceid user has no privilege to delete role with forest client number 00001011
    assert data["detail"]["code"] == ERROR_PERMISSION_REQUIRED
    assert (
        data["detail"]["description"]
        == "Requester has no privilege to grant this access."
    )


def test_delete_user_role_assignment_bceid_cannot_delete_idir_access(
    test_client_fixture: starlette.testclient.TestClient,
    fom_dev_access_admin_token,
    test_rsa_key,
    override_get_verified_target_user,
    override_enforce_bceid_terms_conditions_guard,
):
    """
    test business bceid user cannnot delete idir user access
    """
    # override router guard dependencies
    override_enforce_bceid_terms_conditions_guard()
    override_get_verified_target_user()

    # create a user role assignment for IDIR user
    user_role_xref_id = create_test_user_role_assignment(
        test_client_fixture,
        fom_dev_access_admin_token,
        ACCESS_GRANT_FOM_DEV_CR_IDIR,
    )

    # create a token for business bceid user COGNITO_USERNAME_BCEID with no app admin role,
    # this user has delegated admin privilege which is granted in the local sql
    token = jwt_utils.create_jwt_token(
        test_rsa_key,
        roles=[],
        username=jwt_utils.COGNITO_USERNAME_BCEID_DELEGATED_ADMIN,
    )
    response = test_client_fixture.delete(
        f"{endPoint}/{user_role_xref_id}",
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    data = response.json()
    # business bceid user cannot delete idir user access
    assert data["detail"]["code"] == ERROR_PERMISSION_REQUIRED
    assert (
        data["detail"]["description"]
        == "Business BCEID requester has no privilege to grant this access to IDIR user."
    )


def test_delete_user_role_assignment_bceid_cannot_delete_access_from_diff_org(
    test_client_fixture: starlette.testclient.TestClient,
    fom_dev_access_admin_token,
    test_rsa_key,
    override_get_verified_target_user,
    override_enforce_bceid_terms_conditions_guard,
):
    """
    test business bceid user cannnot delete business bceid user access from different organization
    """
    # override router guard dependencies
    override_enforce_bceid_terms_conditions_guard()
    override_get_verified_target_user(
        {
            **ACCESS_GRANT_FOM_DEV_CR_BCEID_L4T,
            "business_guid": BUSINESS_GUID_BCEID_LOAD_4_TEST,
        }
    )

    # create a user role assignment for a business bceid user from diff organization as the user COGNITO_USERNAME_BCEID
    user_role_xref_id = create_test_user_role_assignment(
        test_client_fixture,
        fom_dev_access_admin_token,
        ACCESS_GRANT_FOM_DEV_CR_BCEID_L4T,  # we created this user with business_guid in local_sql
    )

    # create a token for business bceid user COGNITO_USERNAME_BCEID with no app admin role,
    # this user has delegated admin privilege which is granted in the local sql
    token = jwt_utils.create_jwt_token(
        test_rsa_key,
        roles=[],
        username=jwt_utils.COGNITO_USERNAME_BCEID_DELEGATED_ADMIN,
    )
    response = test_client_fixture.delete(
        f"{endPoint}/{user_role_xref_id}",
        headers=jwt_utils.headers(token),
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() is not None
    data = response.json()
    # business bceid user cannot delete business bceid user access from different organization
    assert data["detail"]["code"] == ERROR_CODE_DIFFERENT_ORG_GRANT_PROHIBITED
    assert (
        data["detail"]["description"]
        == "Managing for different organization is not allowed."
    )


def test_delete_user_role_assignment(
    test_client_fixture: starlette.testclient.TestClient,
    db_pg_session: Session,
    fom_dev_access_admin_token,
    get_current_requester_by_token,
    override_get_verified_target_user,
):
    # override router guard dependencies
    override_get_verified_target_user()

    # create a user role assignment
    response = test_client_fixture.post(
        f"{endPoint}",
        json=ACCESS_GRANT_FOM_DEV_CR_IDIR,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json().get("assignments_detail")
    assert "user_role_xref_id" in data[0]["detail"]

    # verify assignment did get created
    # retrieved requester for current request.
    requester = get_current_requester_by_token(fom_dev_access_admin_token)
    assignment_user_role_items = crud_application.get_application_role_assignments(
        db=db_pg_session,
        application_id=data[0]["detail"]["role"]["application"]["application_id"],
        requester=requester,
    )
    assert len(assignment_user_role_items) == 1
    assert (
        assignment_user_role_items[0].user_role_xref_id
        == data[0]["detail"]["user_role_xref_id"]
    )

    # execute Delete
    response = test_client_fixture.delete(
        f"{endPoint}/{data[0]['detail']['user_role_xref_id']}",
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.NO_CONTENT

    # verify user/role assignment has been deleted
    assignment_user_role_items = crud_application.get_application_role_assignments(
        db=db_pg_session,
        application_id=data[0]["detail"]["role"]["application"]["application_id"],
        requester=requester,
    )
    assert len(assignment_user_role_items) == 0


def test_self_remove_grant_fail(
    test_client_fixture: starlette.testclient.TestClient,
    fom_dev_access_admin_token,
    db_pg_session: Session,
):

    # Setup: the user_role_assignment record already exists
    # It should NOT get deleted
    user = crud_user.get_user_by_cognito_user_id(
        db=db_pg_session, cognito_user_id=jwt_utils.COGNITO_USERNAME
    )
    user_role = crud_user_role.create(
        db=db_pg_session,
        user_id=user.user_id,
        role_id=FOM_DEV_REVIEWER_ROLE_ID,
        requester_cognito_user_id=jwt_utils.COGNITO_USERNAME,
    )

    response = test_client_fixture.delete(
        f"{endPoint}/{user_role.user_role_xref_id}",
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )

    row = db_test_utils.get_user_role_by_cognito_user_id_and_role_id(
        db_pg_session, jwt_utils.COGNITO_USERNAME, FOM_DEV_REVIEWER_ROLE_ID
    )
    assert row is not None, "Expected user role assignment not to be deleted"

    jwt_utils.assert_error_response(response, 403, ERROR_CODE_SELF_GRANT_PROHIBITED)


def test_create_user_role_assignment_many_enforce_bceid_terms_conditions(
    test_client_fixture, test_rsa_key, override_get_verified_target_user
):
    """
    Test this endpoint can "enforce_bceid_terms_conditions" on BCeID
    delegated admin requester when no T&C accepted (record in fam_user_terms_conditions).
    """
    # Use COGNITO_USERNAME_BCEID_DELEGATED_ADMIN as the requester "TEST-3-LOAD-CHILD-1"(BCEID),
    # who is a delegated admin preset at database (flyway) but no T&C record.
    token = jwt_utils.create_jwt_token(
        test_rsa_key,
        roles=[],
        username=jwt_utils.COGNITO_USERNAME_BCEID_DELEGATED_ADMIN,
    )
    # execute create should fail for T&C acceptance.
    response = test_client_fixture.post(
        f"{endPoint}",
        json=ACCESS_GRANT_FOM_DEV_CR_BCEID_L3T,
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() is not None
    assert (
        str(response.json()["detail"]).find(ERROR_CODE_TERMS_CONDITIONS_REQUIRED) != -1
    )

    # Use IDIR delegatged admin as a requester for this endpoint.
    # IDIR delegatged admin does not need T&C accpetance.
    token = jwt_utils.create_jwt_token(
        test_rsa_key,
        roles=[],
        username=jwt_utils.COGNITO_USERNAME_IDIR_DELEGATED_ADMIN,
    )
    # override router guard dependencies
    override_get_verified_target_user()
    response = test_client_fixture.post(
        f"{endPoint}",
        json=ACCESS_GRANT_FOM_DEV_CR_BCEID_L3T,
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.OK


def test_delete_user_role_assignment_enforce_bceid_terms_conditions(
    test_client_fixture: starlette.testclient.TestClient,
    test_rsa_key,
    fom_dev_access_admin_token,
    create_test_user_role_assignments,
):
    # Create users' access grants for FOM_DEV application.
    access_grants_created = create_test_user_role_assignments(
        fom_dev_access_admin_token, [ACCESS_GRANT_FOM_DEV_CR_BCEID_L3T]
    )
    assert len(access_grants_created) == 1

    user_role_xref_id = access_grants_created[0]
    # Use COGNITO_USERNAME_BCEID_DELEGATED_ADMIN as the requester "TEST-3-LOAD-CHILD-1"(BCEID),
    # who is a delegated admin preset at database (flyway) but no T&C record.
    token = jwt_utils.create_jwt_token(
        test_rsa_key,
        roles=[],
        username=jwt_utils.COGNITO_USERNAME_BCEID_DELEGATED_ADMIN,
    )
    # execute delete should fail for T&C acceptance.
    response = test_client_fixture.delete(
        f"{endPoint}/{user_role_xref_id}",
        headers=jwt_utils.headers(token),
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() is not None
    assert (
        str(response.json()["detail"]).find(ERROR_CODE_TERMS_CONDITIONS_REQUIRED) != -1
    )
