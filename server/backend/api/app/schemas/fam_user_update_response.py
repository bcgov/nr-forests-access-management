from typing import List
from pydantic import BaseModel


class FamUserUpdateResponseSchema(BaseModel):
    total_db_users_count: int
    current_page: int
    users_count_on_page: int
    success_user_id_list: List[int]
    failed_user_id_list: List[int]
    ignored_user_id_list: List[int]
    mismatch_user_list: List[int]
