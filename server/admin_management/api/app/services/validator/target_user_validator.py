import copy
import logging

from api.app.constants import (ERROR_CODE_INVALID_REQUEST_PARAMETER,
                               ApiInstanceEnv, IdimSearchUserParamType,
                               UserType)
from api.app.integration.idim_proxy import IdimProxyService
from api.app.schemas.schemas import (IdimProxyBceidSearchParam,
                                     IdimProxySearchParam, Requester,
                                     TargetUser)
from api.app.utils import utils

LOGGER = logging.getLogger(__name__)


class TargetUserValidator:
    def __init__(
        self,
        requester: Requester,
        target_user: TargetUser,
        api_instance_env: ApiInstanceEnv
    ):
        self.verified_target_user = copy.deepcopy(target_user)
        self.idim_proxy_service = IdimProxyService(requester, api_instance_env)

    def verify_user_exist(self) -> TargetUser:
        search_result = None
        if self.verified_target_user.user_type_code == UserType.IDIR:
            # IDIM web service doesn't support search IDIR by user_guid, so we search by userID
            search_result = self.idim_proxy_service.search_idir(
                IdimProxySearchParam(**{"userId": self.verified_target_user.user_name})
            )

            # in edge case, the return guid from search doesn't match the guid given from request parameter
            # this is unlikely to happen if the request comes from frontend because we also validate user in frontend
            # but could happen if make backend api call directly
            if (
                search_result.get("found")
                and search_result.get("guid") != self.verified_target_user.user_guid
            ):
                error_msg = (
                    f"Invalid request, found user {self.verified_target_user.user_name} with user type {self.verified_target_user.user_type_code}, "
                    f"but found user guid {search_result.get('guid')} does not match the user guid in request {self.verified_target_user.user_guid}"
                )
                utils.raise_http_exception(
                    error_code=ERROR_CODE_INVALID_REQUEST_PARAMETER,
                    error_msg=error_msg,
                )

        elif self.verified_target_user.user_type_code == UserType.BCEID:
            search_result = self.idim_proxy_service.search_business_bceid(
                IdimProxyBceidSearchParam(
                    **{
                        "searchUserBy": IdimSearchUserParamType.USER_GUID,
                        "searchValue": self.verified_target_user.user_guid,
                    }
                )
            )

            # in edge case, the return username from search doesn't match the username given from request parameter
            # this is unlikely to happen if the request comes from frontend because we also validate user in frontend
            # but could happen if make backend api call directly
            if (
                search_result.get("found")
                and search_result.get("userId").lower()
                != self.verified_target_user.user_name.lower()
            ):
                error_msg = (
                    f"Invalid request, found user {self.verified_target_user.user_guid} with user type {self.verified_target_user.user_type_code}, "
                    f"but found username {search_result.get('userId').lower()} does not match the username in request {self.verified_target_user.user_name.lower()}"
                )
                utils.raise_http_exception(
                    error_code=ERROR_CODE_INVALID_REQUEST_PARAMETER,
                    error_msg=error_msg,
                )

        # Update various target_user fields from idim search if exists
        if search_result and search_result.get("found"):
            self.verified_target_user.business_guid = search_result.get("businessGuid")
            self.verified_target_user.email = search_result.get("email")
            self.verified_target_user.first_name = search_result.get("firstName")
            self.verified_target_user.last_name = search_result.get("lastName")

        else:
            error_msg = f"Invalid request, cannot find user {self.verified_target_user.user_name} "
            f"{self.verified_target_user.user_guid} with user type {self.verified_target_user.user_type_code}"
            utils.raise_http_exception(
                error_code=ERROR_CODE_INVALID_REQUEST_PARAMETER,
                error_msg=error_msg,
            )

        return self.verified_target_user
