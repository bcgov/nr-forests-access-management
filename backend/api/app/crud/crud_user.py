import datetime
import logging

from api.app.models import model as models
from sqlalchemy.orm import Session, load_only

from .. import schemas
from . import crudUtils as crudUtils

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
    famUser = db.query(models.FamUser).filter(models.FamUser.user_id == user_id).one()
    return famUser

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
    pkColName = crudUtils.getPrimaryKey(models.FamUser)
    nextVal = crudUtils.getNext(models.FamUser, db)

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
