import logging

from api.app import constants as famConstants
from api.app.models import model as models
from sqlalchemy.orm import Session, load_only

from .. import schemas

LOGGER = logging.getLogger(__name__)


def getFamUsers(db: Session):
    """return all the users currently entered into the application

    :param db: _description_
    :type db: Session
    :return: _description_
    :rtype: _type_
    """
    LOGGER.debug(f"db session: {db}")
    famUsers = db.query(models.FamUser).all()
    return famUsers


def getFamUser(db: Session, user_id: int):
    """gets a specific users record

    :param db: _description_
    :type db: Session
    :param user_id: _description_
    :type user_id: int
    :return: _description_
    :rtype: _type_
    """
    # get a single user based on user_id
    famUser = (
        db.query(models.FamUser).filter(models.FamUser.user_id == user_id).one_or_none()
    )
    return famUser


def getFamUserByDomainAndName(
    db: Session, user_type_code: str, user_name: str
) -> models.FamUser:
    # get a single user based on unique combination of user_name and user_type_code.
    fam_user: models.FamUser = (
        db.query(models.FamUser)
        .filter(
            models.FamUser.user_type_code == user_type_code,
            models.FamUser.user_name == user_name,
        )
        .one_or_none()
    )
    LOGGER.debug(
        f"fam_user {str(fam_user.user_id) + ' found' if fam_user else 'not found'}."
    )
    return fam_user


def createFamUser(famUser: schemas.FamUser, db: Session):
    """used to add a new FAM user to the database

    :param famUser: _description_
    :type famUser: schemas.FamUser
    :param db: _description_
    :type db: Session
    :return: _description_
    :rtype: _type_
    """
    LOGGER.debug(f"Creating Fam_User: {famUser}")

    famUserDict = famUser.dict()
    db_item = models.FamUser(**famUserDict)
    db.add(db_item)
    db.flush()
    return db_item


def deleteUser(db: Session, user_id: int):
    """deletes a user

    :param db: _description_
    :type db: Session
    :param user_id: _description_
    :type user_id: int
    :return: _description_
    :rtype: _type_
    """
    famUser = (
        db.query(models.FamUser)
        .options(load_only("user_id"))
        .filter(models.FamUser.user_id == user_id)
        .one()
    )
    db.delete(famUser)
    db.flush()
    return famUser


def findOrCreate(db: Session, user_type_code: str, user_name: str):
    LOGGER.debug(
        f"User - 'findOrCreate' with user_type: {user_type_code}, user_name: {user_name}."
    )

    fam_user = getFamUserByDomainAndName(db, user_type_code, user_name)
    if not fam_user:
        requestUser = schemas.FamUser(
            **{
                "user_type_code": user_type_code,
                "user_name": user_name,
                "create_user": famConstants.FAM_PROXY_API_USER,
            }
        )
        fam_user = createFamUser(requestUser, db)
        LOGGER.debug(f"User created: {fam_user.user_id}.")
        return fam_user

    LOGGER.debug(f"User {fam_user.user_id} found.")
    return fam_user
