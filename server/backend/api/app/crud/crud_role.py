import logging
from typing import Optional
from sqlalchemy.orm import Session

from api.app.models import FamRoleModel
from api.app.schemas import FamRoleCreateSchema, FamForestClientCreateSchema

from . import crud_forest_client


LOGGER = logging.getLogger(__name__)


def get_role(db: Session, role_id: int) -> Optional[FamRoleModel]:
    # get a single role based on role_id
    return db.query(FamRoleModel).filter(FamRoleModel.role_id == role_id).one_or_none()


def create_role(role: FamRoleCreateSchema, db: Session) -> FamRoleModel:
    LOGGER.debug(f"Creating Fam role: {role}")

    fam_role_dict = role.model_dump()
    forest_client_number = fam_role_dict["forest_client_number"]
    del fam_role_dict["forest_client_number"]

    # start by creating a role record
    fam_role_model = FamRoleModel(**fam_role_dict)

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
            fc_pydantic = FamForestClientCreateSchema(**fc_dict)
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


def get_role_by_role_name_and_app_id(
    db: Session, role_name: str, application_id: int
) -> Optional[FamRoleModel]:
    """
    Gets FAM role based on role_name and application_id.
    """
    LOGGER.debug(
        f"Getting FamRole by role_name: {role_name} and application_di: {application_id}"
    )
    return (
        db.query(FamRoleModel)
        .filter(
            FamRoleModel.role_name == role_name,
            FamRoleModel.application_id == application_id,
        )
        .one_or_none()
    )
