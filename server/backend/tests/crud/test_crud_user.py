import logging

from api.app.models import model as model
from api.app.crud import crud_user as crud_user

LOGGER = logging.getLogger(__name__)


def test_getFamUsers_nodata(dbSession):
    """queries for users on an empty database, should return an empty list

    :param dbSession: sql alchemy database session
    :type dbSession: sqlalchemy.orm.Session
    """
    famUsers = crud_user.getFamUsers(dbSession)
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
    users = crud_user.getFamUsers(db)
    LOGGER.debug(f"users: {users}")
    LOGGER.debug(f"number of users: {len(users)}")
    # expecting the number of records in the user table to be 1
    assert 1 == len(users)

    # checking that the expected user is in the db
    for user in users:
        LOGGER.debug(f"user: {user.__dict__} {user.user_name}")
        assert user.user_name == testUserData3["user_name"]


def test_createFamUser(dbSession_famUserTypes, testUserData_asPydantic, deleteAllUsers):
    db = dbSession_famUserTypes
    LOGGER.debug(f"testUserData_asPydantic: {testUserData_asPydantic}")

    # get user count
    userBefore = crud_user.getFamUsers(db)
    numUsersStart = len(userBefore)
    LOGGER.debug(f"testUserData_asPydantic: {testUserData_asPydantic}")
    user = crud_user.createFamUser(famUser=testUserData_asPydantic, db=db)
    LOGGER.debug(f"created the user: {user}")

    # make sure the user that was created has the same guid as the supplied
    # data
    assert user.user_guid == testUserData_asPydantic.user_guid

    #
    usersAfter = crud_user.getFamUsers(db)
    numUsersAfter = len(usersAfter)
    assert numUsersAfter > numUsersStart


def test_getFamUser_withdata(dbSession_famUsers_withdata, testUserData3):
    # test getting a single user
    db = dbSession_famUsers_withdata

    # get one record from db... should only have one
    famUser = db.query(model.FamUser).one()
    LOGGER.debug(f"famUser: {famUser.user_id}")
    crud_user.getFamUser(db=db, user_id=famUser.user_id)
    assert famUser.user_name == testUserData3["user_name"]


def test_deleteFamUsers(dbSession_famUsers_withdata, testUserData2):
    db = dbSession_famUsers_withdata

    # assert that we have a record in the database
    users = crud_user.getFamUsers(db)
    assert 1 == len(users)

    # delete the user from the database
    deleteUser = crud_user.deleteUser(user_id=users[0].user_id, db=db)
    LOGGER.debug(f"deleted user: {deleteUser}")

    # assert no users in the database
    users = users = crud_user.getFamUsers(db)
    assert 0 == len(users)
