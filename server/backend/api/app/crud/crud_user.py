import logging

from api.app import constants as famConstants
from api.app.models import model as models
from sqlalchemy.orm import Session, load_only

from .. import schemas

LOGGER = logging.getLogger(__name__)


def get_users(db: Session):
    """return all the users currently entered into the application

    :param db: _description_
    :type db: Session
    :return: _description_
    :rtype: _type_
    """
    LOGGER.debug(f"db session: {db}")
    fam_users = db.query(models.FamUser).all()
    return fam_users


def get_user(db: Session, user_id: int):
    """gets a specific users record

    :param db: _description_
    :type db: Session
    :param user_id: _description_
    :type user_id: int
    :return: _description_
    :rtype: _type_
    """
    # get a single user based on user_id
    fam_user = (
        db.query(models.FamUser).filter(models.FamUser.user_id == user_id).one_or_none()
    )
    return fam_user


def get_user_by_domain_and_name(
    db: Session, user_type_code: str, user_name: str
) -> models.FamUser:
    # get a single user based on unique combination of user_name and user_type_code.
    fam_user: models.FamUser = (
        db.query(models.FamUser)
        .filter(
            models.FamUser.user_type_code == user_type_code,
            models.FamUser.user_name.ilike(user_name),
        )
        .one_or_none()
    )
    LOGGER.debug(
        f"fam_user {str(fam_user.user_id) + ' found' if fam_user else 'not found'}."
    )
    return fam_user


def create_user(fam_user: schemas.FamUser, db: Session):
    """used to add a new FAM user to the database

    :param fam_user: _description_
    :type fam_user: schemas.FamUser
    :param db: _description_
    :type db: Session
    :return: _description_
    :rtype: _type_
    """
    LOGGER.debug(f"Creating Fam_User: {fam_user}")

    fam_user_dict = fam_user.dict()
    db_item = models.FamUser(**fam_user_dict)
    db.add(db_item)
    db.flush()
    return db_item


def delete_user(db: Session, user_id: int):
    """deletes a user

    :param db: _description_
    :type db: Session
    :param user_id: _description_
    :type user_id: int
    :return: _description_
    :rtype: _type_
    """
    fam_user = (
        db.query(models.FamUser)
        .options(load_only("user_id"))
        .filter(models.FamUser.user_id == user_id)
        .one()
    )
    db.delete(fam_user)
    db.flush()
    return fam_user


def find_or_create(db: Session, user_type_code: str, user_name: str, requester: str):
    LOGGER.debug(
        f"User - 'find_or_create' with user_type: {user_type_code}, " +
        f"user_name: {user_name}."
    )

    fam_user = get_user_by_domain_and_name(db, user_type_code, user_name)
    if not fam_user:
        request_user = schemas.FamUser(
            **{
                "user_type_code": user_type_code,
                "user_name": user_name,
                "create_user": requester
            }
        )
        fam_user = create_user(request_user, db)
        LOGGER.debug(f"User created: {fam_user.user_id}.")
        return fam_user

    LOGGER.debug(f"User {fam_user.user_id} found.")
    return fam_user
