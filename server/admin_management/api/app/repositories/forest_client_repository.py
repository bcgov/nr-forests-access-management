import logging
from sqlalchemy.orm import Session

from api.app.models import model as models
from api.app import schemas


LOGGER = logging.getLogger(__name__)


class ForestClientRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_forest_client_by_number(self, forest_client_number: str) -> models.FamForestClient:
        return (
            self.db.query(models.FamForestClient)
            .filter(models.FamForestClient.forest_client_number == forest_client_number)
            .one_or_none()
        )

    def create_forest_client(
        self, fam_forest_client: schemas.FamForestClientCreate
    ):
        LOGGER.debug(f"Creating Fam_Forest_Client with: {fam_forest_client}")

        db_item = models.FamForestClient(**fam_forest_client)
        self.db.add(db_item)
        self.db.flush()
        return db_item
