import logging
from sqlalchemy.orm import Session

from api.app.schemas import FamForestClientCreate
from api.app.models.model import FamForestClient


LOGGER = logging.getLogger(__name__)


class ForestClientRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_forest_client_by_number(self, forest_client_number: str) -> FamForestClient:
        return (
            self.db.query(FamForestClient)
            .filter(FamForestClient.forest_client_number == forest_client_number)
            .one_or_none()
        )

    def create_forest_client(
        self, fam_forest_client: FamForestClientCreate
    ) -> FamForestClient:
        db_item = FamForestClient(**fam_forest_client)
        self.db.add(db_item)
        self.db.flush()
        return db_item
