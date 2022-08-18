import logging
import datetime

from sqlalchemy import func
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session, load_only
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


def getHighestValue(
    model: sqlalchemy.orm.decl_api.DeclarativeMeta, columnName: str, db: Session
):
    """Queries for the highest value found for a particular column

    :param model: input sqlalchemy model to be queried
    :type model: sqlalchemy.orm.decl_api.DeclarativeMeta
    :param columnName: name of the column who's value we want to retrieve the
        highest existing value
    :type columnName: str
    :param db: sql alchemy database session object
    :type db: Session
    :return: an integer with the current highest value found for the given
        column
    :rtype: int
    """
    columnObj = getattr(model, columnName)
    queryResult = db.query(func.max(columnObj)).first()
    LOGGER.debug(f"queryResult: {queryResult}")
    return queryResult


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
    queryResult = getHighestValue(model, pkName, db)
    if queryResult[0] is None:
        return 1
    else:
        return queryResult[0] + 1


def createFamApplication(famApplication: schemas.FamApplicationCreate, db: Session):
    """used to add a new application record to the database

    :param famApplication: _description_
    :type famApplication: schemas.FamApplication
    :param db: _description_
    :type db: Session
    :return: _description_
    :rtype: _type_
    """
    LOGGER.debug(f"famApplication: {famApplication}")
    LOGGER.debug(f"famApplication as dict: {famApplication.dict()}")

    nextVal = getNext(models.FamApplication, db)
    LOGGER.debug(f"next val: {nextVal}")
    famAppDict = famApplication.dict()
    pkColName = getPrimaryKey(models.FamApplication)
    famAppDict[pkColName] = nextVal

    # TODO: once integrate ian's db changes are merged, the dates will be calced
    #       in the database
    now = datetime.datetime.now()
    famAppDict["create_date"] = now
    famAppDict["update_date"] = now
    famAppDict["update_user"] = getUpdateUser()
    famAppDict["create_user"] = getAddUser()

    # TODO: need to figure out a better way of handling application_client_id is null
    if "application_client_id" in famAppDict:
        del famAppDict["application_client_id"]

    db_item = models.FamApplication(**famAppDict)
    LOGGER.info(f"db_item: {db_item}")
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


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


def getFamApplication(db: Session, application_id: int):
    """gets a single application"""
    application = (
        db.query(models.FamApplication)
        .filter(models.FamApplication.application_id == application_id)
        .one()
    )
    return application


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


def deleteFamApplication(db: Session, application_id: int):
    application = (
        db.query(models.FamApplication)
        .options(load_only("application_id"))
        .filter(models.FamApplication.application_id == application_id)
        .one()
    )
    db.delete(application)

    db.commit()
    return application


def getApplicationByName(db: Session, application_name: str):
    application = (
        db.query(models.FamApplication)
        .filter(models.FamApplication.application_name == application_name)
        .one()
    )
    return application


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


if __name__ == "__main__":
    import database

    db = database.SessionLocal
    getFamApplications(db, 5)
