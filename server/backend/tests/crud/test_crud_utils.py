import logging

import api.app.models.model as model
from api.app.crud import crud_user
from api.app.crud import crud_utils

LOGGER = logging.getLogger(__name__)


def test_get_primary_key():
    """Testing that the method to retrieve the name of a primary key column
    on a table.
    """
    pk_col_name = crud_utils.get_primary_key(model.FamUser)
    assert pk_col_name == "user_id"


def test_get_next(dbsession_fam_users, userdata2_pydantic, delete_all_users):
    """fixture delivers a db session with one record in it, testing that
    the get_next method returns the primary key of the current record + 1

    get_next method was implemented because the unit testing uses sqllite, and
    sqlalchemy wrapper to sqllite does not do the autoincrement / populate of
    primary keys.

    :param dbsession_fam_users: a sql alchemy database session which is
        pre-populated with user data.
    :type dbsession_fam_users: sqlalchemy.orm.Session
    """
    db = dbsession_fam_users
    fam_user_model = model.FamUser
    LOGGER.debug(f"fam_user_model type: {type(fam_user_model)}")
    next_value_before = crud_utils.get_next(db=db, model=fam_user_model)
    assert next_value_before > 0

    # now add record and test again that the number is greater
    crud_user.create_user(famUser=userdata2_pydantic, db=db)

    next_value_after = crud_utils.get_next(db=db, model=fam_user_model)
    assert next_value_after > next_value_before
