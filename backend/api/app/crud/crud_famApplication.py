import datetime
import logging

from api.app.models import model as models
from sqlalchemy.orm import Session, load_only

from .. import schemas
from . import crudUtils as utils

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

    nextVal = utils.getNext(models.FamApplication, db)
    LOGGER.debug(f"next val: {nextVal}")
    famAppDict = famApplication.dict()
    pkColName = utils.getPrimaryKey(models.FamApplication)
    famAppDict[pkColName] = nextVal

    # TODO: once integrate ian's db changes are merged, the dates will be calced
    #       in the database
    now = datetime.datetime.now()
    famAppDict["create_date"] = now
    famAppDict["update_date"] = now
    famAppDict["update_user"] = utils.getUpdateUser()
    famAppDict["create_user"] = utils.getAddUser()

    # TODO: need to figure out a better way of handling application_client_id is null
    if "application_client_id" in famAppDict:
        del famAppDict["application_client_id"]

    db_item = models.FamApplication(**famAppDict)
    LOGGER.info(f"db_item: {db_item}")
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
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


if __name__ == "__main__":
    import database

    db = database.SessionLocal
    getFamApplications(db, 5)