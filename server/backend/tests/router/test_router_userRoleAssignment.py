import copy
import logging

import api.app.models.model as model
import api.app.constants as constants
from api.app.main import apiPrefix
from sqlmodel import Session
import tests.jwt_utils as jwt_utils
import api.app.jwt_validation as jwt_validation

LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/user_role_assignment"

id_claims = jwt_utils.create_jwt_id_claims()
claims = jwt_utils.create_jwt_claims()


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

    claims[jwt_validation.JWT_GROUPS_KEY] = "FOM_ACCESS_ADMIN"
    token = jwt_utils.create_jwt_token(test_rsa_key, claims)
    id_token = jwt_utils.create_jwt_id_token(test_rsa_key, id_claims)

    # Execute POST (concrete role created for role assignment and linked to parent role)
    response = test_client_fixture.post(
        f"{endPoint}",
        json=request_data,
        headers=jwt_utils.headers_with_id_token(token, id_token)
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

    claims[jwt_validation.JWT_GROUPS_KEY] = "FOM_ACCESS_ADMIN"
    token = jwt_utils.create_jwt_token(test_rsa_key, claims)
    id_token = jwt_utils.create_jwt_id_token(test_rsa_key, id_claims)

    # Execute POST (role assignment created)
    response = test_client_fixture.post(
        f"{endPoint}",
        json=request_data,
        headers=jwt_utils.headers_with_id_token(token, id_token)
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
