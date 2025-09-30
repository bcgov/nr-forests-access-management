from abc import ABC

from api.app.crud import crud_utils
from api.app.schemas.requester import RequesterSchema


class ExtAPIInterface(ABC):
    """
    Interface for external API services.
    """

    def __init__(self, requester: RequesterSchema, application_id: int, db=None, *args, **kwargs):
        self.requester = requester
        self.application_id = application_id
        self.db = db
        super().__init__()

    def is_request_allowed(self) -> bool:
        """
        Default implementation to validate if the external request is allowed to call the API.
        Returns:
            bool: True if allowed, False otherwise.
        """
        return crud_utils.allow_ext_call_api_permission(
            db=self.db, application_id=self.application_id, user_name=self.requester.user_name
        )
