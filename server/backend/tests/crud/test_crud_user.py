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


def test_getFamUsers_withdata(dbsession_fam_users, user_data3_dict):
    """gets a database session which has user data inserted into it, and a
    dictionary containing the data that was added to the database

    :param dbsession_fam_users: sql alchemy database session
    :type dbsession_fam_users: sqlalchemy.orm.Session
    :param user_data3_dict: _description_
    :type user_data3_dict: _type_
    """
    db = dbsession_fam_users
    users = crud_user.getFamUsers(db)
    LOGGER.debug(f"users: {users}")
    LOGGER.debug(f"number of users: {len(users)}")
    # expecting the number of records in the user table to be 1
    assert 1 == len(users)

    # checking that the expected user is in the db
    for user in users:
        LOGGER.debug(f"user: {user.__dict__} {user.user_name}")
        assert user.user_name == user_data3_dict["user_name"]


def test_createFamUser(dbsession_fam_user_types, userdata_pydantic, delete_all_users):
    db = dbsession_fam_user_types
    LOGGER.debug(f"userdata_pydantic: {userdata_pydantic}")

    # get user count
    userBefore = crud_user.getFamUsers(db)
    numUsersStart = len(userBefore)
    LOGGER.debug(f"userdata_pydantic: {userdata_pydantic}")
    user = crud_user.createFamUser(famUser=userdata_pydantic, db=db)
    LOGGER.debug(f"created the user: {user}")

    # make sure the user that was created has the same guid as the supplied
    # data
    assert user.user_guid == userdata_pydantic.user_guid

    #
    usersAfter = crud_user.getFamUsers(db)
    numUsersAfter = len(usersAfter)
    assert numUsersAfter > numUsersStart


def test_getFamUser_withdata(dbsession_fam_users, user_data3_dict):
    # test getting a single user
    db = dbsession_fam_users

    # get one record from db... should only have one
    famUser = db.query(model.FamUser).one()
    LOGGER.debug(f"famUser: {famUser.user_id}")
    crud_user.getFamUser(db=db, user_id=famUser.user_id)
    assert famUser.user_name == user_data3_dict["user_name"]


def test_deleteFamUsers(dbsession_fam_users, userData2_Dict):
    db = dbsession_fam_users

    # assert that we have a record in the database
    users = crud_user.getFamUsers(db)
    assert 1 == len(users)

    # delete the user from the database
    deleteUser = crud_user.deleteUser(user_id=users[0].user_id, db=db)
    LOGGER.debug(f"deleted user: {deleteUser}")

    # assert no users in the database
    users = users = crud_user.getFamUsers(db)
    assert 0 == len(users)
