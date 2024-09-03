import logging

from api.app.models import FamForestClientModel
from sqlalchemy.orm import Session

from api.app.schemas import FamForestClientCreateSchema

LOGGER = logging.getLogger(__name__)


def get_forest_client(db: Session, forest_client_number: str) -> FamForestClientModel:
    LOGGER.debug(
        "Forest Client - 'get_forest_client' with forest_client_number: "
        f"{forest_client_number}."
    )
    fam_forest_client = (
        db.query(FamForestClientModel)
        .filter(FamForestClientModel.forest_client_number == forest_client_number)
        .one_or_none()
    )
    LOGGER.debug(f"fam_forest_client: {fam_forest_client}")
    return fam_forest_client


def create_forest_client(fam_forest_client: FamForestClientCreateSchema, db: Session):
    LOGGER.debug(f"Creating Fam_Forest_Client with: {fam_forest_client}")

    fam_forest_client_dict = fam_forest_client.model_dump()
    db_item = FamForestClientModel(**fam_forest_client_dict)
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

        request_forest_client = FamForestClientCreateSchema(
            **{
                "forest_client_number": forest_client_number,
                "create_user": requester,
            }
        )
        fam_forest_client = create_forest_client(request_forest_client, db)
        LOGGER.debug(f"New Forest_Client added: {fam_forest_client.client_number_id}.")
        return fam_forest_client

    LOGGER.debug(f"Forest_Client {fam_forest_client.client_number_id} found.")
    return fam_forest_client
