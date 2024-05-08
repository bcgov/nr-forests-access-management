import logging
from sqlalchemy.orm import Session

from api.app.schemas import FamForestClientCreateDto
from api.app.repositories.forest_client_repository import ForestClientRepository


LOGGER = logging.getLogger(__name__)


class ForestClientService:
    def __init__(self, db: Session):
        self.forest_client_repository = ForestClientRepository(db)

    def get_forest_client_by_number(self, forest_client_number: str):
        return self.forest_client_repository.get_forest_client_by_number(
            forest_client_number
        )

    def find_or_create(self, forest_client_number: str, requester: str):
        fam_forest_client = self.get_forest_client_by_number(forest_client_number)
        if not fam_forest_client:
            LOGGER.debug(
                f"Forest Client with forest_client_number {forest_client_number} "
                "does not exist, add a new Forest Client."
            )

            request_forest_client = FamForestClientCreateDto(
                **{
                    "forest_client_number": forest_client_number,
                    "create_user": requester,
                }
            )

            fam_forest_client = self.forest_client_repository.create_forest_client(
                request_forest_client
            )
            LOGGER.debug(
                f"New Forest_Client added: {fam_forest_client.client_number_id}."
            )
            return fam_forest_client

        LOGGER.debug(f"Forest_Client {fam_forest_client.client_number_id} found.")
        return fam_forest_client
