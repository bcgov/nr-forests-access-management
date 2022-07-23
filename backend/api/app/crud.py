import datetime
import logging

from sqlalchemy import func
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session
import sqlalchemy.orm.decl_api

from . import schemas
from .models import model as models

LOGGER = logging.getLogger(__name__)


def getFamApplications(db: Session):
    """runs query to return all the community health service areas and the
    metadata about how many times they have been queried and when

    :param db: database session
    :type db: Session
    :return: list of sql alchemy data objects
    :rtype: list
    """
    LOGGER.debug("running getFamApplications")
    LOGGER.debug(f"db: {type(db)}")
    # LOGGER.debug(f"db parameters {db.parameters}")
    famApps = db.query(models.FamApplication).all()
    LOGGER.debug(f"famApplications: {famApps}, {type(famApps)}")
    return famApps


def getPrimaryKey(model: models) -> str:
    """recieves a declarative base model and returns the primary key that
    is defined for the base

    :param model: input declarative base model object
    :type model: sqlalchemy.ext.declarative
    :return: name of the primarly key column as a string
    :rtype: str
    """
    pkName = inspect(model).primary_key[0].name
    LOGGER.debug(f"primary key for table {model.__table__}: {pkName}")
    return pkName


def getNext(model: sqlalchemy.orm.decl_api.DeclarativeMeta, db: Session) -> int:
    """calculates the next increment for the given model.  This is
    created because in development the autoincrement / populate feature
    for sqllite databases does not always work.

    :param model: input declarative base model
    :type model: sqlalchemy.orm.decl_api.DeclarativeMeta
    :param db: sql alchemy database session object
    :type db: sqlalchemy.orm.session.Session
    :return: the next value for the primary key
    :rtype: int
    """
    pkName = getPrimaryKey(model)
    columnObj = getattr(model, pkName)
    queryResult = db.query(func.max(columnObj)).first()
    LOGGER.debug(f"queryResult: {queryResult}")
    if queryResult[0] is None:
        return 1
    else:
        return queryResult[0] + 1


def createFamApplication(famApplication: schemas.FamApplication, db: Session):
    LOGGER.debug(f"famApplication: {famApplication}")
    LOGGER.debug(f"famApplication as dict: {famApplication.dict()}")
    pkColName = getPrimaryKey(models.FamApplication)
    nextVal = getNext(models.FamApplication, db)
    LOGGER.debug(f"next val: {nextVal}")

    famAppDict = famApplication.dict()
    famAppDict[pkColName] = nextVal

    db_item = models.FamApplication(**famAppDict)
    LOGGER.info(f"db_item: {db_item}")
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def createFamUser(famUser: schemas.FamUser, db: Session):
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
    db.refresh(db_item)
    return db_item


def getFamUsers(db: Session):
    LOGGER.debug(f"db session: {db}")
    famUsers = db.query(models.FamUser).all()
    return famUsers


def getFamUser(db: Session, user_id: int):
    # get a single user based on user_id
    famUser = db.query(models.FamUser).filter(models.FamUser.user_id == user_id).one()
    return famUser


def deleteUser(db: Session, user_id: int):
    famUser = db.query(models.FamUser).filter(models.FamUser.user_id == user_id).one()
    db.delete(famUser)
    db.commit()
    return famUser


def createFamRole(famRole: schemas.FamRole, db: Session):
    LOGGER.debug(f"Fam role: {famRole}")
    pkColName = getPrimaryKey(models.FamRole)
    nextVal = getNext(models.FamRole, db)

    famRoleDict = famRole.dict()
    famRoleDict[pkColName] = nextVal

    # maybe there is a way to get the db to do this for us, but just as easy
    # to add the dates in here.
    now = datetime.datetime.now()
    famRoleDict["create_date"] = now
    famRoleDict["update_date"] = now

    LOGGER.debug(f"famRoleDict: {famRoleDict}")
    LOGGER.debug(
        f"famAppDict: {famRoleDict['create_date']} {famRoleDict['update_date']}"
    )

    db_item = models.FamRole(**famRoleDict)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def getFamRoles(db: Session):
    LOGGER.debug(f"db session: {db}")
    famRoles = db.query(models.FamRole).all()
    return famRoles


def getFamRole(db: Session, role_id: int):
    # get a single role based on role_id
    schemas.FamRole = db.query(models.FamRole).filter(models.FamRole.role_id == role_id).one()
    return schemas.FamRole


if __name__ == "__main__":
    import database

    db = database.SessionLocal
    getFamApplications(db, 5)
