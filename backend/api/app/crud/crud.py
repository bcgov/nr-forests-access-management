import datetime
import logging

import sqlalchemy.orm.decl_api
from api.app.models import model as models
from sqlalchemy import func
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session, load_only

from .. import schemas

LOGGER = logging.getLogger(__name__)



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

