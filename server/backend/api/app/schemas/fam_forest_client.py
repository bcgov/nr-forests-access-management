import logging
from typing import Optional
from pydantic import BaseModel, ConfigDict, StringConstraints
from typing_extensions import Annotated
from api.app.constants import FOREST_CLIENT_STATUS

from .fam_forest_client_status import FamForestClientStatusSchema

LOGGER = logging.getLogger(__name__)


class FamForestClientSchema(BaseModel):

    client_name: Optional[Annotated[str, StringConstraints(max_length=60)]] = None
    forest_client_number: Annotated[str, StringConstraints(max_length=8)]
    status: Optional[FamForestClientStatusSchema] = None

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def from_api_json(json_dict):
        LOGGER.debug(f"from_api_json - {json_dict}")
        client_name = json_dict["clientName"]
        forest_client_number = json_dict["clientNumber"]
        forest_client_status_code = json_dict[FOREST_CLIENT_STATUS["KEY"]]
        status = FamForestClientStatusSchema.to_fam_status(forest_client_status_code)
        fc = FamForestClientSchema(
            client_name=client_name,
            forest_client_number=forest_client_number,
            status=status,
        )
        return fc
