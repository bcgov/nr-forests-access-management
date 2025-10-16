import logging

import api.app.models.model as model
import pytest
from api.app.constants import UserType
from api.app.crud import crud_user, crud_utils
from api.app.models.model import FamApplication, FamRole, FamUserRoleXref
from api.app.schemas import FamUserSchema
from sqlalchemy.orm import Session
from testspg.constants import (FOM_DEV_APPLICATION_ID, TEST_CREATOR,
                               TEST_NEW_USER, TEST_USER_GUID_IDIR)

LOGGER = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "str_list_to_test, expcted_str_list",
    [
        (["fam", "fom", "aws"], ["FAM", "FOM", "AWS"]),
        (["FAM", "FOM", "AWS"], ["FAM", "FOM", "AWS"]),
        (None, None),
    ],
)
def test_to_upper(str_list_to_test, expcted_str_list):
    result = crud_utils.to_upper(str_list_to_test)
    if result:
        for index, r in enumerate(result):
            assert r == expcted_str_list[index]
    else:
        assert result == expcted_str_list


@pytest.mark.parametrize(
    "str_list_to_test, str_to_replace, replace_with, expcted_str_list",
    [
        (
            ["FAM_ADMIN", "FOM_DEV_ADMIN", "FOM_TEST_ADMIN"],
            "_ADMIN",
            "",
            ["FAM", "FOM_DEV", "FOM_TEST"],
        ),
        (
            ["FAM_ACCESS", "FOM_DEV", "FOM"],
            "_ACCESS",
            "_ADMIN",
            ["FAM_ADMIN", "FOM_DEV", "FOM"],
        ),
        (None, "something", "some_other_thing", None),
    ],
)
def test_replace_str_list(
    str_list_to_test, str_to_replace, replace_with, expcted_str_list
):
    result = crud_utils.replace_str_list(str_list_to_test, str_to_replace, replace_with)
    if result:
        for index, r in enumerate(result):
            assert r == expcted_str_list[index]
    else:
        assert result == expcted_str_list


def test_get_primary_key():
    """Testing that the method to retrieve the name of a primary key column
    on a table.
    """
    pk_col_name = crud_utils.get_primary_key(model.FamUser)
    assert pk_col_name == "user_id"


def test_get_next(db_pg_session: Session):
    """fixture delivers a db session with one record in it, testing that
    the get_next method returns the primary key of the current record + 1

    get_next method was implemented because the unit testing uses sqllite, and
    sqlalchemy wrapper to sqllite does not do the autoincrement / populate of
    primary keys.

    :param dbsession_fam_users: a sql alchemy database session which is
        pre-populated with user data.
    :type dbsession_fam_users: sqlalchemy.orm.Session
    """
    fam_user_model = model.FamUser
    LOGGER.debug(f"fam_user_model type: {type(fam_user_model)}")
    next_value_before = crud_utils.get_next(db=db_pg_session, model=fam_user_model)
    assert next_value_before > 0

    # now add record and test again that the number is greater
    request_user = FamUserSchema(**TEST_NEW_USER)
    new_user = crud_user.create_user(fam_user=request_user, db=db_pg_session)

    next_value_after = crud_utils.get_next(db=db_pg_session, model=fam_user_model)
    assert next_value_after > next_value_before


def test_allow_ext_call_api_permission_true(db_pg_session, setup_new_user):
    """
    Test that allow_ext_call_api_permission returns True when user has a role with call_api_flag=True for the application.
    """

    # Setup: create application, role with call_api_flag=True, and assign to user
    app = db_pg_session.query(FamApplication).filter_by(application_id=FOM_DEV_APPLICATION_ID).first()
    user = setup_new_user(**{ "user_type": UserType.IDIR,  "user_name": "test_user", "user_guid": TEST_USER_GUID_IDIR })
    role = FamRole(
        role_name="TEST_ROLE",
        application_id=app.application_id,
        role_type_code="C",
        call_api_flag=True,
        create_user=TEST_CREATOR,
    )
    db_pg_session.add(role)
    db_pg_session.flush()
    xref = FamUserRoleXref(user_id=user.user_id, role_id=role.role_id, create_user=TEST_CREATOR)
    db_pg_session.add(xref)
    db_pg_session.flush()

    # Should return True
    assert crud_utils.allow_ext_call_api_permission(db_pg_session, app.application_id, user.user_name) is True


def test_allow_ext_call_api_permission_false(db_pg_session, setup_new_user):
    app = db_pg_session.query(FamApplication).filter_by(application_id=FOM_DEV_APPLICATION_ID).first()
    user = setup_new_user(**{ "user_type": UserType.IDIR,  "user_name": "test_user", "user_guid": TEST_USER_GUID_IDIR })
    role = FamRole(
        role_name="TEST_ROLE",
        application_id=app.application_id,
        role_type_code="C",
        call_api_flag=False,
        create_user=TEST_CREATOR,
    )
    db_pg_session.add(role)
    db_pg_session.flush()
    xref = FamUserRoleXref(user_id=user.user_id, role_id=role.role_id, create_user=TEST_CREATOR)
    db_pg_session.add(xref)
    db_pg_session.flush()
    # Should return False
    assert crud_utils.allow_ext_call_api_permission(db_pg_session, app.application_id, user.user_name) is False