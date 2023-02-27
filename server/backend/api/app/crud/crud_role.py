import logging
from typing import List, Optional

from api.app.models import model as models
from sqlalchemy.orm import Session
import api.app.constants as constants

from .. import schemas
from . import crud_forest_client


LOGGER = logging.getLogger(__name__)


def get_role(db: Session, role_id: int) -> Optional[models.FamRole]:
    # get a single role based on role_id
    return (
        db.query(models.FamRole).filter(models.FamRole.role_id == role_id).one_or_none()
    )


def get_roles(db: Session) -> List[models.FamRole]:
    """gets all the existing FAM roles

    :param db: _description_
    :type db: Session
    :return: _description_
    :rtype: _type_
    """
    LOGGER.debug(f"db session: {db}")
    return db.query(models.FamRole).all()


def create_role(role: schemas.FamRoleCreate, db: Session) -> models.FamRole:
    LOGGER.debug(f"Creating Fam role: {role}")

    fam_role_dict = role.dict()
    forest_client_number = fam_role_dict["forest_client_number"]
    del fam_role_dict["forest_client_number"]

    # start by creating a role record
    fam_role_model = models.FamRole(**fam_role_dict)

    if forest_client_number:
        # need to create a forest client record

        # check if a forest client record already exists
        forest_client_record = crud_forest_client.get_forest_client(
            db, forest_client_number
        )

        # if no forest client record is found then create one
        if not forest_client_record:
            LOGGER.debug("creating a forest client record")
            fc_dict = {
                "forest_client_number": forest_client_number,
                "client_name": "going to delete anyways when complete issue"
                + f" 327 / {forest_client_number}",
                "create_user": fam_role_model.create_user,
            }
            fc_pydantic = schemas.FamForestClientCreate(**fc_dict)
            forest_client_model = crud_forest_client.create_forest_client(
                db=db, fam_forest_client=fc_pydantic
            )
            LOGGER.debug(
                "forest client id: " + f"{forest_client_model.client_number_id}"
            )

            # finally add the forests client record to the role
            fam_role_model.client_number = forest_client_model
        else:
            fam_role_model.client_number = forest_client_record

    db.add(fam_role_model)
    db.flush()
    return fam_role_model


def get_role_by_role_name(db: Session, role_name: str) -> Optional[models.FamRole]:
    """
    Gets FAM roles by unique role_name
    """
    LOGGER.debug(f"Getting FamRole by role_name: {role_name}")
    return (
        db.query(models.FamRole)
        .filter(models.FamRole.role_name == role_name)
        .one_or_none()
    )
