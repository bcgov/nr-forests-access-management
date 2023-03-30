import logging
import pytest
from sqlalchemy.orm import Session
import api.app.models.model as model
import api.app.schemas as schemas
from api.app.crud import crud_user
from api.app.crud import crud_utils
from testspg.constants import TEST_NEW_USER

LOGGER = logging.getLogger(__name__)


@pytest.mark.parametrize("str_list_to_test, expcted_str_list",[
    (['fam', 'fom', 'aws'], ['FAM', 'FOM', 'AWS']),
    (['FAM', 'FOM', 'AWS'], ['FAM', 'FOM', 'AWS']),
    (None, None)
])
def test_to_upper(str_list_to_test, expcted_str_list):
    result = crud_utils.to_upper(str_list_to_test)
    if result:
        for index, r in enumerate(result):
            assert r == expcted_str_list[index]
    else:
        assert result == expcted_str_list


@pytest.mark.parametrize("str_list_to_test, str_to_replace, replace_with, expcted_str_list", [
    (
        ['FAM_ACCESS_ADMIN', 'FOM_DEV_ACCESS_ADMIN', 'FOM_TEST_ACCESS_ADMIN'],
        "_ACCESS_ADMIN", "",
        ['FAM', 'FOM_DEV', 'FOM_TEST']
    ),
    (
        ['FAM_ACCESS', 'FOM_DEV', 'FOM'],
        "_ACCESS", "_ACCESS_ADMIN",
        ['FAM_ACCESS_ADMIN', 'FOM_DEV', 'FOM']
    ),
    (None, "something", "some_other_thing", None)
])
def test_replace_str_list(
    str_list_to_test,
    str_to_replace,
    replace_with,
    expcted_str_list
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


def test_get_next(db_pg_connection: Session):
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
    next_value_before = crud_utils.get_next(db=db_pg_connection, model=fam_user_model)
    assert next_value_before > 0

    # now add record and test again that the number is greater
    request_user = schemas.FamUser(
        **TEST_NEW_USER
    )
    new_user = crud_user.create_user(fam_user=request_user, db=db_pg_connection)

    next_value_after = crud_utils.get_next(db=db_pg_connection, model=fam_user_model)
    assert next_value_after > next_value_before

    # clean up
    crud_user.delete_user(db_pg_connection, new_user.user_id)


def test_get_application_id_from_name(
    db_pg_connection: Session
):
    # get non exists application
    application_id = crud_utils.get_application_id_from_name(
        db_pg_connection,
        "TEST"
    )
    assert application_id is None

    # get FAM application id
    application_id = crud_utils.get_application_id_from_name(
        db_pg_connection,
        "FAM"
    )
    assert application_id == 1
