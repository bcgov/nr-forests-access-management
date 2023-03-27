import copy
import logging

import api.app.constants as constants
import api.app.jwt_validation as jwt_validation
import api.app.models.model as model
import tests.jwt_utils as jwt_utils
import tests.tests.test_constants as testConstants
from api.app.main import apiPrefix
from sqlmodel import Session

LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/user_role_assignment"


def test_create_user_role_assignment_associated_with_abstract_role(
    test_client_fixture,
    dbsession_fam_user_types,
    dbsession_FOM_submitter_role,  # noqa NOSONAR
    user_role_dict,
    clean_up_all_user_role_assignment,
    test_rsa_key
):
    db: Session = dbsession_FOM_submitter_role

    # Verify no assignment initially.
    user_role_assignment_db_items = db.query(model.FamUserRoleXref).all()
    assert len(user_role_assignment_db_items) == 0

    # Verify FOM submitter abstract role exists initially.
    fom_submitter_role: model.FamRole = (
        db.query(model.FamRole).filter(model.FamRole.role_name == "FOM_Submitter").one()
    )
    assert fom_submitter_role is not None
    assert fom_submitter_role.role_type_code == constants.RoleType.ROLE_TYPE_ABSTRACT

    request_data = copy.deepcopy(user_role_dict)
    request_data["role_id"] = fom_submitter_role.role_id

    claims = jwt_utils.create_jwt_claims()
    claims[jwt_validation.JWT_GROUPS_KEY] = "FOM_ACCESS_ADMIN"
    token = jwt_utils.create_jwt_token(test_rsa_key, claims)

    # Execute POST (concrete role created for role assignment and linked to parent role)
    response = test_client_fixture.post(
        f"{endPoint}",
        json=request_data,
        headers=jwt_utils.headers(token)
    )

    # Verify status and body
    assert response.status_code == 200
    assert response.json() is not None

    # Verify assignment did get created
    assignment_id = response.json()["user_role_xref_id"]
    assignment_db_item: model.FamUserRoleXref = (
        db.query(model.FamUserRoleXref)
        .filter(model.FamUserRoleXref.user_role_xref_id == assignment_id)
        .one()
    )
    assert assignment_db_item is not None

    # Verify assignment linking to correct user
    assignment_user_db_item = (
        db.query(model.FamUser)
        .filter(model.FamUser.user_name == request_data["user_name"])
        .one()
    )
    assert assignment_user_db_item is not None

    # Verify assignment linking to correct role and parent role
    assignment_role_db_item: model.FamRole = (
        db.query(model.FamRole)
        .filter(model.FamRole.role_id == assignment_db_item.role_id)
        .one()
    )
    assert assignment_role_db_item is not None
    assert assignment_role_db_item.parent_role_id == fom_submitter_role.role_id


def test_create_user_role_assignment_with_concrete_role(
    test_client_fixture,
    dbsession_fam_user_types,
    dbsession_concrete_role,
    user_role_dict,
    clean_up_all_user_role_assignment,
    test_rsa_key
):
    db = dbsession_concrete_role

    # Verify no assignment initially.
    user_role_assignment_db_items = db.query(model.FamUserRoleXref).all()
    assert len(user_role_assignment_db_items) == 0

    # Verify one concrete role exists initially.
    role_db_item: model.FamRole = db.query(model.FamRole).one()
    assert role_db_item is not None
    assert role_db_item.role_type_code == constants.RoleType.ROLE_TYPE_CONCRETE

    request_data = copy.deepcopy(user_role_dict)
    request_data["role_id"] = role_db_item.role_id
    del request_data["forest_client_number"]

    claims = jwt_utils.create_jwt_claims()
    claims[jwt_validation.JWT_GROUPS_KEY] = ["FOM_ACCESS_ADMIN"]
    token = jwt_utils.create_jwt_token(test_rsa_key, claims)

    # Execute POST (role assignment created)
    response = test_client_fixture.post(
        f"{endPoint}",
        json=request_data,
        headers=jwt_utils.headers(token)
    )

    # Verify status and body
    assert response.status_code == 200
    assert response.json() is not None

    # Verify assignment did get created
    assignment_id = response.json()["user_role_xref_id"]
    assignment_db_item: model.FamUserRoleXref = (
        db.query(model.FamUserRoleXref)
        .filter(model.FamUserRoleXref.user_role_xref_id == assignment_id)
        .one()
    )
    assert assignment_db_item is not None

    # Verify assignment linking to correct user
    assignment_user_db_item = (
        db.query(model.FamUser)
        .filter(model.FamUser.user_name == request_data["user_name"])
        .one()
    )
    assert assignment_user_db_item is not None

    # Verify assignment linking to correct role and no parent role
    assignment_role_db_item: model.FamRole = (
        db.query(model.FamRole)
        .filter(model.FamRole.role_id == assignment_db_item.role_id)
        .one()
    )
    assert assignment_role_db_item is not None
    assert assignment_role_db_item.parent_role_id is None


def test_delete_user_role_assignment(
    test_client_fixture, dbsession_user_role_assignment, test_rsa_key
):
    db = dbsession_user_role_assignment

    # Verify 1 user/role assignment initially
    user_role_assignment_db_items = db.query(
        model.FamUserRoleXref
    ).all()
    assert len(user_role_assignment_db_items) == 1

    claims = jwt_utils.create_jwt_claims()
    claims[jwt_validation.JWT_GROUPS_KEY] = "FOM_ACCESS_ADMIN"
    token = jwt_utils.create_jwt_token(test_rsa_key, claims)

    # Execute Delete
    test_client_fixture.delete(
        f"{endPoint}/{user_role_assignment_db_items[0].user_role_xref_id}",
        headers=jwt_utils.headers(token)
    )

    # Verify user/role assignment has been deleted
    user_role_assignment_db_items: model.FamUserRoleXref = db.query(
        model.FamUserRoleXref
    ).all()
    assert len(user_role_assignment_db_items) == 0


def test_assign_same_application_roles_for_different_environments(
    test_client_fixture,
    dbsession_fam_user_types,
    dbsession_fom_submitter_role_dev_test,
    user_role_dict,
    clean_up_all_user_role_assignment,
    test_rsa_key
):
    db: Session = dbsession_fom_submitter_role_dev_test

    # Verify no assignment initially.
    user_role_assignment_db_items = db.query(model.FamUserRoleXref).all()
    assert len(user_role_assignment_db_items) == 0

    # Verify setup correctly
    fom_dev_application: model.FamApplication = (
        db.query(model.FamApplication)
        .filter(
            model.FamApplication.app_environment == constants.AppEnv.APP_ENV_TYPE_DEV)
        .one()
    )
    fom_test_application: model.FamApplication = (
        db.query(model.FamApplication)
        .filter(
            model.FamApplication.app_environment == constants.AppEnv.APP_ENV_TYPE_TEST)
        .one()
    )
    assert fom_dev_application.application_name == testConstants.FOM_APP_DEV_NAME
    assert fom_test_application.application_name == testConstants.FOM_APP_TEST_NAME

    fom_dev_submitter_role: model.FamRole = (
        db.query(model.FamRole)
        .filter(
            model.FamRole.role_name == testConstants.FOM_SUBMITTER_ROLE_NAME,
            model.FamRole.application_id == fom_dev_application.application_id)
        .one()
    )
    fom_test_submitter_role: model.FamRole = (
        db.query(model.FamRole)
        .filter(
            model.FamRole.role_name == testConstants.FOM_SUBMITTER_ROLE_NAME,
            model.FamRole.application_id == fom_test_application.application_id)
        .one()
    )

    # Prepare dev, test data
    request_dev_data = copy.deepcopy(user_role_dict)
    request_dev_data["role_id"] = fom_dev_submitter_role.role_id
    request_test_data = copy.deepcopy(user_role_dict)
    request_test_data["role_id"] = fom_test_submitter_role.role_id

    claims = jwt_utils.create_jwt_claims()
    claims[jwt_validation.JWT_GROUPS_KEY] = ["FOM_DEV_ACCESS_ADMIN", "FOM_TEST_ACCESS_ADMIN"]
    token = jwt_utils.create_jwt_token(test_rsa_key, claims)

    # Execute POST (fom_dev)
    response_dev = test_client_fixture.post(
        f"{endPoint}",
        json=request_dev_data,
        headers=jwt_utils.headers(token)
    )
    # Verify dev request status
    assert response_dev.status_code == 200
    assert response_dev.json() is not None

    # Execute POST (fom_test)
    response_test = test_client_fixture.post(
        f"{endPoint}",
        json=request_test_data,
        headers=jwt_utils.headers(token)
    )
    # Verify test request status
    assert response_test.status_code == 200
    assert response_test.json() is not None

    assignment_user_role_id_dev = response_dev.json()["user_role_xref_id"]
    assignment_user_role_id_test = response_test.json()["user_role_xref_id"]
    assert assignment_user_role_id_dev != assignment_user_role_id_test

    assignment_role_id_dev = response_dev.json()["role_id"]
    assignment_role_id_test = response_test.json()["role_id"]
    assert assignment_role_id_dev != assignment_role_id_test  # Verify assignment id not the same.

    assignment_role_dev_db_item: model.FamRole = (
        db.query(model.FamRole)
        .filter(model.FamRole.role_id == assignment_role_id_dev)
        .one()
    )
    assignment_role_test_db_item: model.FamRole = (
        db.query(model.FamRole)
        .filter(model.FamRole.role_id == assignment_role_id_test)
        .one()
    )
    # Verify role with associated parent role and application.
    assert assignment_role_id_dev != fom_dev_submitter_role.role_id
    assert assignment_role_id_test != fom_test_submitter_role.role_id
    assert assignment_role_dev_db_item.parent_role_id == fom_dev_submitter_role.role_id
    assert assignment_role_test_db_item.parent_role_id == fom_test_submitter_role.role_id
    assert assignment_role_dev_db_item.application.application_name ==\
        fom_dev_application.application_name
    assert assignment_role_test_db_item.application.application_name ==\
        fom_test_application.application_name

    # Execute Delete dev_role assignment
    test_client_fixture.delete(
        f"{endPoint}/{assignment_user_role_id_dev}",
        headers=jwt_utils.headers(token)
    )

    # Verify correctly delet user/role assignment
    user_role_assignment_db_items: model.FamUserRoleXref = db.query(
        model.FamUserRoleXref
    ).all()
    assert len(user_role_assignment_db_items) == 1
    assert user_role_assignment_db_items[0].role_id != assignment_role_id_dev