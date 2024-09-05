from typing import List, Union

from pydantic import BaseModel, ConfigDict, StringConstraints
from typing_extensions import Annotated
from api.app.constants import UserType

# Role assignment with one role at a time for the user.
class FamUserRoleAssignmentCreateSchema(BaseModel):
    user_name: Annotated[
        str, StringConstraints(min_length=3, max_length=20)
    ]  # IDIM search max length
    user_guid: Annotated[str, StringConstraints(min_length=32, max_length=32)]
    user_type_code: UserType
    role_id: int
    forest_client_numbers: Union[
        List[Annotated[str, StringConstraints(min_length=1, max_length=8)]], None
    ] = None
    requires_send_user_email: bool = False

    model_config = ConfigDict(from_attributes=True)
