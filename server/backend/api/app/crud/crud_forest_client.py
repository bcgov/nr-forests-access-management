import logging

from api.app import constants as famConstants
from api.app.models import model as models
from sqlalchemy.orm import Session

from .. import schemas

LOGGER = logging.getLogger(__name__)


def get_forest_client(db: Session, forest_client_number: str) -> models.FamForestClient:
    LOGGER.debug(
        "Forest Client - 'get_forest_client' with forest_client_number: "
        f"{forest_client_number}."
    )
    fam_forest_client = (
        db.query(models.FamForestClient)
        .filter(models.FamForestClient.forest_client_number == forest_client_number)
        .one_or_none()
    )
    LOGGER.debug(f"fam_forest_client: {fam_forest_client}")
    return fam_forest_client


def create_forest_client(fam_forest_client: schemas.FamForestClientCreate, db: Session):
    LOGGER.debug(f"Creating Fam_Forest_Client with: {fam_forest_client}")

    fam_forest_client_dict = fam_forest_client.dict()
    db_item = models.FamForestClient(**fam_forest_client_dict)
    db.add(db_item)
    db.flush()
    return db_item


def find_or_create(db: Session, forest_client_number: str, requester: str):
    LOGGER.debug(
        "Forest Client - 'find_or_create' with forest_client_number: "
        f"{forest_client_number}."
    )

    fam_forest_client = get_forest_client(db, forest_client_number)
    if not fam_forest_client:
        LOGGER.debug(
            f"Forest Client with forest_client_number {forest_client_number} "
            "does not exist, add a new Forest Client."
        )

        request_forest_client = schemas.FamForestClientCreate(
            **{
                "forest_client_number": forest_client_number,
                #"client_name": client_name,
                "create_user": requester,
            }
        )
        fam_forest_client = create_forest_client(request_forest_client, db)
        LOGGER.debug(f"New Forest_Client added: {fam_forest_client.client_number_id}.")
        return fam_forest_client

    LOGGER.debug(f"Forest_Client {fam_forest_client.client_number_id} found.")
    return fam_forest_client
