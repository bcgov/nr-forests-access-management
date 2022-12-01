import datetime
import logging
from typing import List, Union

from api.app.models import model as models
from sqlalchemy.orm import Session, load_only

from .. import schemas
from . import crudUtils as crudUtils

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

def getFamApplication(db: Session, application_id: int):
    """gets a single application"""
    application = (
        db.query(models.FamApplication)
        .filter(models.FamApplication.application_id == application_id)
        .one()
    )
    return application

def getApplicationByName(db: Session, application_name: str):
    application = (
        db.query(models.FamApplication)
        .filter(models.FamApplication.application_name == application_name)
        .one()
    )
    return application


def createFamApplication(
        famApplication: schemas.FamApplicationCreate,
        db: Session) -> models.FamApplication:
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

    nextVal = crudUtils.getNext(models.FamApplication, db)
    LOGGER.debug(f"next val: {nextVal}")
    famAppDict = famApplication.dict()
    pkColName = crudUtils.getPrimaryKey(models.FamApplication)
    famAppDict[pkColName] = nextVal

    # TODO: once integrate ian's db changes are merged, the dates will be calced
    #       in the database
    now = datetime.datetime.now()
    famAppDict["create_date"] = now
    famAppDict["update_date"] = now
    famAppDict["update_user"] = crudUtils.getUpdateUser()
    famAppDict["create_user"] = crudUtils.getAddUser()

    # TODO: need to figure out a better way of handling application_client_id is null
    if "application_client_id" in famAppDict:
        del famAppDict["application_client_id"]

    db_item = models.FamApplication(**famAppDict)
    LOGGER.info(f"db_item: {db_item}")
    db.add(db_item)
    db.flush()
    # db.refresh(db_item)
    return db_item

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


def getFamApplicationRoles(
        db: Session,
        application_id: int) -> List[schemas.FamApplicationRole]:
    """Given a database session and an application id, will return a roles that
    have been defined for the application id.  Currently does not return any
    child roles.

    :param db: input database session object
    :param application_id: the application id who's roles are to be retrieved
    :return: orm FamRole model listing related roles that have been created
             for the given application.
    """
    application = (
        db.query(models.FamRole)
        # .join(models.FamRole)
        # .options(load_only("application_id"))
        .filter(models.FamRole.application_id == application_id,
                models.FamRole.parent_role_id == None)
        .all()
    )
    return application

def getFamApplicationRoleAssignments(db: Session, application_id: int):
    """_summary_

    :param db: _description_
    :param application_id: _description_
    :return: _description_

    * query application table relates to roles that relates to user-role xref
      that relates to users
      FamApplication ->
        FamRole ->
            FamUserRoleXref ->
                FamUser
    """
    # TODO: define return type
    # TODO: complete doc string
    LOGGER.debug(f"app id: {application_id}")

    # query application for Roles / user role xref / users
    # asking for one() as there should only be one application record where
    # application_id == {app_id}
    # application = (
    #     db.query(models.FamApplication)
    #     .filter(models.FamApplication.application_id == application_id)
    #     .one()
    # )

    # roles = (
    #     db.query(models.FamRole)
    #     .filter(models.FamRole.application_id == application_id)
    #     .all()
    # )

    # TODO: apply join conditions to avoid cartesian product
    crossref = (
        db.query(models.FamUserRoleXref)
        .filter(models.FamRole.application_id == application_id).all()
    )

    LOGGER.debug(f"crossref: {crossref}")
    return crossref

if __name__ == "__main__":
    import database

    db = database.SessionLocal
    getFamApplications(db, 5)