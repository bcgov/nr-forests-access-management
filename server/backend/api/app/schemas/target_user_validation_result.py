from typing import List
from pydantic import BaseModel
from api.app.schemas import TargetUserSchema

class TargetUserValidationResultSchema(BaseModel):
    verified_users: List[TargetUserSchema]
    failed_users: List[TargetUserSchema]
