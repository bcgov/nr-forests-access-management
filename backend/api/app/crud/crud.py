import logging
import datetime

from sqlalchemy import func
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session, load_only
import sqlalchemy.orm.decl_api

from .. import schemas
from api.app.models import model as models

LOGGER = logging.getLogger(__name__)









def createFamUser(famUser: schemas.FamUser, db: Session):
    """used to add a new FAM user to the database

    :param famUser: _description_
    :type famUser: schemas.FamUser
    :param db: _description_
    :type db: Session
    :return: _description_
    :rtype: _type_
    """
    LOGGER.debug(f"Fam user: {famUser}")
    pkColName = getPrimaryKey(models.FamUser)
    nextVal = getNext(models.FamUser, db)

    famUserDict = famUser.dict()
    famUserDict[pkColName] = nextVal

    # maybe there is a way to get the db to do this for us, but just as easy
    # to add the dates in here.
    now = datetime.datetime.now()
    famUserDict["create_date"] = now
    famUserDict["update_date"] = now

    LOGGER.debug(f"famUserDict: {famUserDict}")
    LOGGER.debug(
        f"famAppDict: {famUserDict['create_date']} {famUserDict['update_date']}"
    )

    db_item = models.FamUser(**famUserDict)
    db.add(db_item)
    db.commit()
    # db.refresh(db_item)
    return db_item


def createFamGroup(famGroup: schemas.FamGroupPost, db: Session):
    """used to add a new FAM group to the database

    :param famGroup: _description_
    :type famGroup: schemas.FamGroupPost
    :param db: _description_
    :type db: Session
    :return: _description_
    :rtype: _type_
    """
    pkColName = getPrimaryKey(models.FamGroup)
    nextVal = getNext(models.FamGroup, db)
    famGroupDict = famGroup.dict()
    famGroupDict[pkColName] = nextVal

    now = datetime.datetime.now()
    famGroupDict["create_date"] = now
    famGroupDict["update_date"] = now

    db_item = models.FamGroup(**famGroupDict)
    db.add(db_item)
    db.commit()
    # db.refresh(db_item)
    return db_item


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
    famUser = db.query(models.FamUser).filter(models.FamUser.user_id == user_id).one()
    return famUser





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

    db.commit()
    return famUser






def getUpdateUser():
    """A stub method, once the api has been integrated w/ Cognito the update
    user will come from the JWT token that is a result of the authentication.
    """
    return "default updateuser"


def getAddUser():
    """A stub method, once the api has been integrated w/ Cognito the update
    user will come from the JWT token that is a result of the authentication.
    """
    return "default adduser"


def getFamRole(db: Session, role_id: int):
    # get a single role based on role_id
    schemas.FamRole = db.query(models.FamRole).filter(models.FamRole.role_id == role_id).one()
    return schemas.FamRole


def getFamRoles(db: Session):
    """gets all the existing FAM roles

    :param db: _description_
    :type db: Session
    :return: _description_
    :rtype: _type_
    """
    LOGGER.debug(f"db session: {db}")
    famRoles = db.query(models.FamRole).all()
    return famRoles


def createFamRole(famRole: schemas.FamRole, db: Session):
    LOGGER.debug(f"Fam role: {famRole}")

    famRoleDict = famRole.dict()
    LOGGER.debug(f"famRoleDict: {famRoleDict}")

    db_item = models.FamRole(**famRoleDict)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

