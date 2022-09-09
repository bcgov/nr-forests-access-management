import logging

from api.app.models import model as models
from sqlalchemy.orm import Session

from .. import schemas

LOGGER = logging.getLogger(__name__)


def getFamRole(db: Session, role_id: int) -> models.FamRole:
    # get a single role based on role_id
    return db.query(models.FamRole).filter(
        models.FamRole.role_id == role_id).one()


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
