from pydantic import BaseModel, StringConstraints
from typing_extensions import Annotated

from api.app.constants import (
    FOREST_CLIENT_STATUS,
    DESCRIPTION_ACTIVE,
    DESCRIPTION_INACTIVE,
    FamForestClientStatusType,
)


# This is not an object from FAM model. It is an helper class to map Forest Client API
# client status into FAM's status needs (Active/Inactive).
class FamForestClientStatusSchema(BaseModel):

    status_code: FamForestClientStatusType
    description: Annotated[str, StringConstraints(max_length=10)]

    @staticmethod
    def to_fam_status(forest_client_status_code: str):
        # Map Forest Client API's 'clientStatusCode' to FAM
        accepted_api_active_codes = [FOREST_CLIENT_STATUS["CODE_ACTIVE"]]
        status_code = (
            FamForestClientStatusType.ACTIVE
            if forest_client_status_code in accepted_api_active_codes
            else FamForestClientStatusType.INACTIVE
        )
        description = (
            DESCRIPTION_ACTIVE
            if status_code == FamForestClientStatusType.ACTIVE
            else DESCRIPTION_INACTIVE
        )
        status = FamForestClientStatusSchema(
            status_code=status_code, description=description
        )
        return status
