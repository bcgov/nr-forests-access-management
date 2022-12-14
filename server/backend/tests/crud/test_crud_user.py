import logging

from api.app.models import model as model
from api.app.crud import crud_user as crud_user

LOGGER = logging.getLogger(__name__)


def test_get_users_nodata(dbsession):
    """queries for users on an empty database, should return an empty list

    :param dbsession: sql alchemy database session
    :type dbsession: sqlalchemy.orm.Session
    """
    fam_users = crud_user.get_users(dbsession)
    LOGGER.debug(f"fam users: {fam_users}")
    assert fam_users == []


def test_get_users_with_data(dbsession_fam_users, user_data3_dict):
    """gets a database session which has user data inserted into it, and a
    dictionary containing the data that was added to the database

    :param dbsession_fam_users: sql alchemy database session
    :type dbsession_fam_users: sqlalchemy.orm.Session
    :param user_data3_dict: _description_
    :type user_data3_dict: _type_
    """
    db = dbsession_fam_users
    users = crud_user.get_users(db)
    LOGGER.debug(f"users: {users}")
    LOGGER.debug(f"number of users: {len(users)}")
    # expecting the number of records in the user table to be 1
    assert 1 == len(users)

    # checking that the expected user is in the db
    for user in users:
        LOGGER.debug(f"user: {user.__dict__} {user.user_name}")
        assert user.user_name == user_data3_dict["user_name"]


def test_create_user(dbsession_fam_user_types, userdata_pydantic, delete_all_users):
    db = dbsession_fam_user_types
    LOGGER.debug(f"userdata_pydantic: {userdata_pydantic}")

    # get user count
    user_before = crud_user.get_users(db)
    num_users_start = len(user_before)
    LOGGER.debug(f"userdata_pydantic: {userdata_pydantic}")
    user = crud_user.create_user(famUser=userdata_pydantic, db=db)
    LOGGER.debug(f"created the user: {user}")

    # make sure the user that was created has the same guid as the supplied
    # data
    assert user.user_guid == userdata_pydantic.user_guid

    #
    users_after = crud_user.get_users(db)
    num_users_after = len(users_after)
    assert num_users_after > num_users_start


def test_get_fam_user_with_data(dbsession_fam_users, user_data3_dict):
    # test getting a single user
    db = dbsession_fam_users

    # get one record from db... should only have one
    fam_user = db.query(model.FamUser).one()
    LOGGER.debug(f"fam_user: {fam_user.user_id}")
    crud_user.get_user(db=db, user_id=fam_user.user_id)
    assert fam_user.user_name == user_data3_dict["user_name"]


def test_delete_fam_users(dbsession_fam_users, user_data2_dict):
    db = dbsession_fam_users

    # assert that we have a record in the database
    users = crud_user.get_users(db)
    assert 1 == len(users)

    # delete the user from the database
    delete_user = crud_user.delete_user(user_id=users[0].user_id, db=db)
    LOGGER.debug(f"deleted user: {delete_user}")

    # assert no users in the database
    users = users = crud_user.get_users(db)
    assert 0 == len(users)
