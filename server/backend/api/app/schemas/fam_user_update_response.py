from datetime import datetime
from typing import List

from pydantic import BaseModel


class FamUserUpdateResponseSchema(BaseModel):
    total_db_users_count: int
    current_page: int
    users_count_on_page: int
    run_on: datetime
    elapsed: str
    success_user_update_list: List[dict]
    failed_user_update_list: List[dict]
    ignored_user_update_list: List[dict]
    mismatch_user_update_list: List[dict]
