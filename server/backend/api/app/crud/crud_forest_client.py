import logging

from api.app import constants as famConstants
from api.app.models import model as models
from sqlalchemy.orm import Session

from .. import schemas

LOGGER = logging.getLogger(__name__)


def getFamForestClient(db: Session, client_number_id: int):
    LOGGER.debug(
        f"Forest Client - 'getFamForestClient' with client_number_id: {client_number_id}."
    )
    return (
        db.query(models.FamForestClient)
        .filter(models.FamForestClient.client_number_id == client_number_id)
        .one_or_none()
    )


def createFamForestClient(famForestClient: schemas.FamForestClientCreate, db: Session):
    LOGGER.debug(f"Creating Fam_Forest_Client with: {famForestClient}")

    fam_forest_client_dict = famForestClient.dict()
    db_item = models.FamForestClient(**fam_forest_client_dict)
    db.add(db_item)
    db.flush()
    return db_item


def findOrCreate(
    db: Session,
    client_number_id: int,
    client_name: str = famConstants.DUMMY_FOREST_CLIENT_NAME,
):
    LOGGER.debug(
        f"Forest Client - 'findOrCreate' with client_number_id: {client_number_id}."
    )

    fam_forest_client = getFamForestClient(db, client_number_id)
    if not fam_forest_client:
        LOGGER.debug(
            f"Forest Client with Id {client_number_id} "
            "does not exist, add a new Forest Client."
        )
        request_forest_client = schemas.FamForestClientCreate(
            **{
                "client_number_id": client_number_id,
                "client_name": client_name,
                "create_user": famConstants.FAM_PROXY_API_USER,
            }
        )
        fam_forest_client = createFamForestClient(request_forest_client, db)
        LOGGER.debug(f"New Forest_Client added: {fam_forest_client.client_number_id}.")
        return fam_forest_client

    LOGGER.debug(f"Forest_Client {fam_forest_client.client_number_id} found.")
    return fam_forest_client
