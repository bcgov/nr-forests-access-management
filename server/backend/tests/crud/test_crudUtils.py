
import logging

import api.app.models.model as model
from api.app.crud import crud_user, crudUtils

LOGGER = logging.getLogger(__name__)

def test_getPrimaryKey():
    """Testing that the method to retrieve the name of a primary key column
    on a table.
    """
    pkColName = crudUtils.getPrimaryKey(model.FamUser)
    assert pkColName == "user_id"

def test_getNext(dbsession_fam_users, userdata2_pydantic, delete_all_users):
    """fixture delivers a db session with one record in it, testing that
    the getNext method returns the primary key of the current record + 1

    getNext method was implemented because the unit testing uses sqllite, and
    sqlalchemy wrapper to sqllite does not do the autoincrement / populate of
    primary keys.

    :param dbsession_fam_users: a sql alchemy database session which is
        pre-populated with user data.
    :type dbsession_fam_users: sqlalchemy.orm.Session
    """
    db = dbsession_fam_users
    famUserModel = model.FamUser
    LOGGER.debug(f"famUserModel type: {type(famUserModel)}")
    nextValueBefore = crudUtils.getNext(db=db, model=famUserModel)
    assert nextValueBefore > 0

    # now add record and test again that the number is greater
    crud_user.createFamUser(famUser=userdata2_pydantic, db=db)

    nextValueAfter = crudUtils.getNext(db=db, model=famUserModel)
    assert nextValueAfter > nextValueBefore
