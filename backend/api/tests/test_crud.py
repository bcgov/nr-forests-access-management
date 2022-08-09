import logging
import os

import api.app.crud as crud
import api.app.models.model

LOGGER = logging.getLogger(__name__)


def test_getFamApplications_nodata(dbSession):
    """Was a starting place to figure out crud tests that work with the database
    session, not complete.  Assumes the database starts without any data.

    :param dbSession: sql alchemy database session
    :type dbSession: sqlalchemy.orm.Session
    """
    # TODO: start coding tests for crud.py code.
    files = os.listdir(".")
    LOGGER.debug(f"files: {files}")

    famApps = crud.getFamApplications(dbSession)
    assert famApps == []
    LOGGER.debug(f"famApps: {famApps}")


def test_getFamUsers_nodata(dbSession):
    """queries for users on an empty database, should return an empty list

    :param dbSession: sql alchemy database session
    :type dbSession: sqlalchemy.orm.Session
    """
    famUsers = crud.getFamUsers(dbSession)
    LOGGER.debug(f"fam users: {famUsers}")
    assert famUsers == []


def test_getFamUsers_withdata(dbSession_famUsers_withdata, testUserData3):
    """gets a database session which has user data inserted into it, and a
    dictionary containing the data that was added to the database

    :param dbSession_famUsers_withdata: sql alchemy database session
    :type dbSession_famUsers_withdata: sqlalchemy.orm.Session
    :param testUserData3: _description_
    :type testUserData3: _type_
    """
    db = dbSession_famUsers_withdata
    users = crud.getFamUsers(db)
    LOGGER.debug(f"users: {users}")
    LOGGER.debug(f"number of users: {len(users)}")
    # expecting the number of records in the user table to be 1
    assert 1 == len(users)

    # checking that the expected user is in the db
    for user in users:
        LOGGER.debug(f"user: {user.__dict__} {user.user_name}")
        assert user.user_name == testUserData3["user_name"]


def test_createFamUser(testUserData_asPydantic, dbSession, deleteAllUsers):
    db = dbSession
    LOGGER.debug(f"testUserData_asPydantic: {testUserData_asPydantic}")

    # get user count
    userBefore = crud.getFamUsers(db)
    numUsersStart = len(userBefore)
    LOGGER.debug(f"testUserData_asPydantic: {testUserData_asPydantic}")
    user = crud.createFamUser(famUser=testUserData_asPydantic, db=db)
    LOGGER.debug(f"created the user: {user}")

    # make sure the user that was created has the same guid as the supplied
    # data
    assert user.user_guid == testUserData_asPydantic.user_guid

    #
    usersAfter = crud.getFamUsers(db)
    numUsersAfter = len(usersAfter)
    assert numUsersAfter > numUsersStart


def test_getFamUser_withdata(dbSession_famUsers_withdata, testUserData3):
    # test getting a single user
    db = dbSession_famUsers_withdata

    # get one record from db... should only have one
    famUser = db.query(api.app.models.model.FamUser).one()
    LOGGER.debug(f"famUser: {famUser.user_id}")
    crud.getFamUser(db=db, user_id=famUser.user_id)
    assert famUser.user_name == testUserData3["user_name"]


def test_deleteFamUsers(dbSession_famUsers_withdata, testUserData2):
    db = dbSession_famUsers_withdata

    # assert that we have a record in the database
    users = crud.getFamUsers(db)
    assert 1 == len(users)

    # delete the user from the database
    deleteUser = crud.deleteUser(user_id=users[0].user_id, db=db)
    LOGGER.debug(f"deleted user: {deleteUser}")

    # assert no users in the database
    users = users = crud.getFamUsers(db)
    assert 0 == len(users)


def test_getPrimaryKey():
    """Testing that the method to retrieve the name of a primary key column
    on a table.
    """
    pkColName = crud.getPrimaryKey(api.app.models.model.FamUser)
    assert pkColName == "user_id"


def test_getNext(dbSession_famUsers_withdata, testUserData2_asPydantic, deleteAllUsers):
    """fixture delivers a db session with one record in it, testing that
    the getNext method returns the primary key of the current record + 1

    getNext method was implemented because the unit testing uses sqllite, and
    sqlalchemy wrapper to sqllite does not do the autoincrement / populate of
    primary keys.

    :param dbSession_famUsers_withdata: a sql alchemy database session which is
        pre-populated with user data.
    :type dbSession_famUsers_withdata: sqlalchemy.orm.Session
    """
    db = dbSession_famUsers_withdata
    famUserModel = api.app.models.model.FamUser
    LOGGER.debug(f"famUserModel type: {type(famUserModel)}")
    nextValueBefore = crud.getNext(db=db, model=famUserModel)
    assert nextValueBefore > 0

    # now add record and test again that the number is greater
    crud.createFamUser(famUser=testUserData2_asPydantic, db=db)

    nextValueAfter = crud.getNext(db=db, model=famUserModel)
    assert nextValueAfter > nextValueBefore


def test_getFamRoles_nodata(dbSession):
    famRoles = crud.getFamRoles(dbSession)
    LOGGER.debug(f"fam roles: {famRoles}")
    assert famRoles == []


def test_getFamRoles_withdata(dbSession_famRoles_withdata, testRoleData):
    db = dbSession_famRoles_withdata
    roles = crud.getFamRoles(db)
    LOGGER.debug(f"roles: {roles}")
    LOGGER.debug(f"number of roles: {len(roles)}")
    # expecting the number of records in the role table to be 1
    assert 1 == len(roles)

    # checking that the expected user is in the db
    for role in roles:
        LOGGER.debug(f"role: {role.__dict__} {role.role_name}")
        assert role.role_name == testRoleData["role_name"]
