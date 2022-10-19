import logging

from api.app import constants as famConstants
from api.app.models import model as models
from sqlalchemy.orm import Session

from .. import schemas

LOGGER = logging.getLogger(__name__)


def getFamForestClient(
    db: Session, forest_client_number: str
) -> models.FamForestClient:
    LOGGER.debug(
        "Forest Client - 'getFamForestClient' with forest_client_number: "
        f"{forest_client_number}."
    )
    return (
        db.query(models.FamForestClient)
        .filter(models.FamForestClient.forest_client_number == forest_client_number)
        .one_or_none()
    )


def createFamForestClient(famForestClient: schemas.FamForestClientCreate, db: Session):
    LOGGER.debug(f"Creating Fam_Forest_Client with: {famForestClient}")

    fam_forest_client_dict = famForestClient.dict()
    db_item = models.FamForestClient(**fam_forest_client_dict)
    db.add(db_item)
    db.flush()
    return db_item


def findOrCreate(db: Session, forest_client_number: str, client_name: str):
    LOGGER.debug(
        "Forest Client - 'findOrCreate' with forest_client_number: "
        f"{forest_client_number}."
    )

    fam_forest_client = getFamForestClient(db, forest_client_number)
    if not fam_forest_client:
        LOGGER.debug(
            f"Forest Client with forest_client_number {forest_client_number} "
            "does not exist, add a new Forest Client."
        )

        request_forest_client = schemas.FamForestClientCreate(
            **{
                "forest_client_number": forest_client_number,
                "client_name": client_name,
                "create_user": famConstants.FAM_PROXY_API_USER,
            }
        )
        fam_forest_client = createFamForestClient(request_forest_client, db)
        LOGGER.debug(f"New Forest_Client added: {fam_forest_client.client_number_id}.")
        return fam_forest_client

    LOGGER.debug(f"Forest_Client {fam_forest_client.client_number_id} found.")
    return fam_forest_client
