from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, StringConstraints
from typing_extensions import Annotated

from api.app.constants import UserType


class FamUserSchema(BaseModel):
    user_type_code: UserType
    cognito_user_id: Optional[Annotated[str, StringConstraints(max_length=100)]] = (
        None  # temporarily optional
    )
    user_name: Annotated[str, StringConstraints(max_length=20)]
    user_guid: Union[
        Annotated[str, StringConstraints(min_length=32, max_length=32)], None
    ]
    create_user: Annotated[str, StringConstraints(max_length=100)]
    update_user: Optional[Annotated[str, StringConstraints(max_length=100)]] = None

    model_config = ConfigDict(from_attributes=True)
