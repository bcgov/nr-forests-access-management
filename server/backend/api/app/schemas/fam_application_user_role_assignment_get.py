from pydantic import BaseModel, ConfigDict
from .fam_user_info import FamUserInfoSchema
from .fam_role_with_client import FamRoleWithClientSchema

class FamApplicationUserRoleAssignmentGetSchema(BaseModel):
    user_role_xref_id: int
    user_id: int
    role_id: int
    user: FamUserInfoSchema
    role: FamRoleWithClientSchema

    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(from_attributes=True)
