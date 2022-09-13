import logging
from typing import List, Optional

from api.app.models import model as models
from sqlalchemy.orm import Session

from .. import schemas

LOGGER = logging.getLogger(__name__)


def getFamRole(db: Session, role_id: int) -> Optional[models.FamRole]:
    # get a single role based on role_id
    return db.query(models.FamRole).filter(
        models.FamRole.role_id == role_id).one_or_none()


def getFamRoles(db: Session) -> List[models.FamRole]:
    """gets all the existing FAM roles

    :param db: _description_
    :type db: Session
    :return: _description_
    :rtype: _type_
    """
    LOGGER.debug(f"db session: {db}")
    return db.query(models.FamRole).all()


def createFamRole(famRole: schemas.FamRole, db: Session) -> models.FamRole:
    LOGGER.debug(f"Creating Fam role: {famRole}")

    famRoleDict = famRole.dict()
    db_item = models.FamRole(**famRoleDict)
    db.add(db_item)
    # db.commit()
    # db.refresh(db_item)
    db.flush()
    return db_item


def getFamRoleByRoleName(
    db: Session, role_name: str
) -> Optional[models.FamRole]:
    """
    Gets FAM roles by unique role_name
    """
    LOGGER.debug(f"Getting FamRole by role_name: {role_name}")
    return (
        db.query(models.FamRole)
        .filter(models.FamRole.role_name == role_name)
        .one_or_none()
    )
