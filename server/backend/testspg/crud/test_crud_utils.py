import logging
import pytest
from api.app.models import FamUserModel
from api.app.schemas import FamUserSchema
from api.app.crud import crud_user, crud_utils
from sqlalchemy.orm import Session
from testspg.constants import TEST_NEW_USER

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
    pk_col_name = crud_utils.get_primary_key(FamUserModel)
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
    fam_user_model = FamUserModel
    LOGGER.debug(f"fam_user_model type: {type(fam_user_model)}")
    next_value_before = crud_utils.get_next(db=db_pg_session, model=fam_user_model)
    assert next_value_before > 0

    # now add record and test again that the number is greater
    request_user = FamUserSchema(**TEST_NEW_USER)
    new_user = crud_user.create_user(fam_user=request_user, db=db_pg_session)

    next_value_after = crud_utils.get_next(db=db_pg_session, model=fam_user_model)
    assert next_value_after > next_value_before
