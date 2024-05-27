import logging

from api.app.integration.idim_proxy import IdimProxyService
from api.app.constants import (
    IdimSearchUserParamType,
    UserType,
    ERROR_CODE_INVALID_REQUEST_PARAMETER,
)
from api.app.schemas import (
    IdimProxySearchParam,
    IdimProxyBceidSearchParam,
    Requester,
    TargetUser,
)
from api.app.utils import utils


LOGGER = logging.getLogger(__name__)


class IdimValidator:
    def __init__(self, requester: Requester, target_user: TargetUser):
        self.user_type_code = target_user.user_type_code
        self.user_name = target_user.user_name
        self.user_guid = target_user.user_guid
        self.idim_proxy_service = IdimProxyService(requester)

    def verify_user_exist(self):
        search_result = None
        if self.user_type_code == UserType.IDIR:
            # IDIM web service doesn't support search IDIR by user_guid, so we search by userID
            search_result = self.idim_proxy_service.search_idir(
                IdimProxySearchParam(**{"userId": self.user_name})
            )

            # in edge case, the return guid from search doesn't match the guid given from request parameter
            # this is unlikely to happen if the request comes from frontend because we also validate user in frontend
            # but could happen if make backend api call directly
            if (
                search_result.get("found")
                and search_result.get("guid").lower() != self.user_guid.lower()
            ):
                error_msg = (
                    f"Invalid request, found user {self.user_name} with user type {self.user_type_code}, "
                    f"but found user guid {search_result.get('guid').lower()} does not match the user guid in request {self.user_guid.lower()}"
                )
                utils.raise_http_exception(
                    error_code=ERROR_CODE_INVALID_REQUEST_PARAMETER,
                    error_msg=error_msg,
                )

        elif self.user_type_code == UserType.BCEID:
            search_result = self.idim_proxy_service.search_business_bceid(
                IdimProxyBceidSearchParam(
                    **{
                        "searchUserBy": IdimSearchUserParamType.USER_GUID,
                        "searchValue": self.user_guid,
                    }
                )
            )

            # in edge case, the return username from search doesn't match the username given from request parameter
            # this is unlikely to happen if the request comes from frontend because we also validate user in frontend
            # but could happen if make backend api call directly
            if (
                search_result.get("found")
                and search_result.get("userId").lower() != self.user_name.lower()
            ):
                error_msg = (
                    f"Invalid request, found user {self.user_guid} with user type {self.user_type_code}, "
                    f"but found username {search_result.get('userId').lower()} does not match the username in request {self.user_name.lower()}"
                )
                utils.raise_http_exception(
                    error_code=ERROR_CODE_INVALID_REQUEST_PARAMETER,
                    error_msg=error_msg,
                )

        if not search_result or not search_result.get("found"):
            error_msg = f"Invalid request, cannot find user {self.user_name} {self.user_guid} with user type {self.user_type_code}"
            utils.raise_http_exception(
                error_code=ERROR_CODE_INVALID_REQUEST_PARAMETER,
                error_msg=error_msg,
            )

        return search_result
