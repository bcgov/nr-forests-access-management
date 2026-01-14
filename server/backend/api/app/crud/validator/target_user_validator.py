import copy
import logging

from api.app.constants import (ERROR_CODE_INVALID_REQUEST_PARAMETER,
                               ApiInstanceEnv, IdimSearchUserParamType,
                               UserType)
from api.app.integration.idim_proxy import IdimProxyService
from api.app.schemas import (IdimProxyBceidSearchParamSchema,
                             IdimProxySearchParamSchema, RequesterSchema,
                             TargetUserSchema)
from api.app.utils import utils
from api.app.models.model import FamRole
from api.app.schemas.target_user_validation_result import FailedTargetUserSchema, TargetUserValidationResultSchema
from server.backend.api.app.crud import crud_utils

LOGGER = logging.getLogger(__name__)

class TargetUserValidator:
    def __init__(
        self,
        requester: RequesterSchema,
        target_user: TargetUserSchema,
        api_instance_env: ApiInstanceEnv,
    ):
        LOGGER.debug(f"Validating target_user - {target_user.user_id}, target env set to: {api_instance_env}")
        self.verified_target_user = copy.deepcopy(target_user)
        self.idim_proxy_service = IdimProxyService(requester, api_instance_env)

    def verify_user_exist(self) -> TargetUserSchema:
        search_result = None
        if self.verified_target_user.user_type_code == UserType.IDIR:
            # IDIM web service doesn't support search IDIR by user_guid, so we search by userID
            search_result = self.idim_proxy_service.search_idir(
                IdimProxySearchParamSchema(
                    **{"userId": self.verified_target_user.user_name}
                )
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
                IdimProxyBceidSearchParamSchema(
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

            if search_result.get("found") and search_result.get("businessGuid"):
                self.verified_target_user.business_guid = search_result.get(
                    "businessGuid"
                )

        # Update various target_user fields from idim search if exists
        if search_result and search_result.get("found"):
            self.verified_target_user.business_guid = search_result.get("businessGuid")
            self.verified_target_user.first_name = search_result.get("firstName")
            self.verified_target_user.last_name = search_result.get("lastName")
            self.verified_target_user.email = search_result.get("email")

        else:
            error_msg = (
                f"Invalid request, cannot find user {self.verified_target_user.user_name} "
                f"{self.verified_target_user.user_guid} with user type {self.verified_target_user.user_type_code}"
            )
            utils.raise_http_exception(
                error_code=ERROR_CODE_INVALID_REQUEST_PARAMETER,
                error_msg=error_msg,
            )

        return self.verified_target_user


def validate_target_users(
    requester: RequesterSchema,
    target_users: list[TargetUserSchema],
    role: FamRole
) -> TargetUserValidationResultSchema:
    """
    Validate a list of target users by calling the IDIM web service.

    For each user in the provided list, this function verifies their existence and updates
    business GUID and other user details as needed (especially for BCeID users). If a user
    is invalid or cannot be verified, it is added to the failed_users list; otherwise, it is added to verified_users.

    Parameters:
        requester (RequesterSchema): The user making the request, used for context and authorization.
        target_users (list[TargetUserSchema]): The list of users to be validated.
        role (FamRole): The application role context for the validation.

    Returns:
        TargetUserValidationResult: An object containing lists of verified and failed TargetUserSchema objects.
    """
    LOGGER.debug(f"Validating {len(target_users)} target users for application: {role.application}")
    api_instance_env = crud_utils.use_api_instance_by_app(role.application)
    verified_users = []
    failed_users = []
    for target_user in target_users:
        try:
            target_user_validator = TargetUserValidator(requester, target_user, api_instance_env)
            verified_user = target_user_validator.verify_user_exist()
            verified_users.append(verified_user)
        except Exception as e:
            LOGGER.error(f"Validation failed for user {target_user.user_name}: {str(e)}")
            failed_users.append(FailedTargetUserSchema(user=target_user, error_reason=str(e)))

    return TargetUserValidationResultSchema(verified_users=verified_users, failed_users=failed_users)


def validate_bceid_same_org(requester: RequesterSchema, target_users: list[TargetUserSchema]):
    """
    Validate that the requester (BCeID user) can only manage target users from the same organization.
    Raises ValueError if validation fails.
    """
    if requester.user_type_code == UserType.BCEID:
        requester_business_guid = requester.business_guid

        for target_user in target_users:
            target_user_business_guid = target_user.business_guid

            if requester_business_guid is None or target_user_business_guid is None:
                raise ValueError("Requester or target user business GUID is missing.")

            if requester_business_guid.upper() != target_user_business_guid.upper():
                raise ValueError(f"Managing user {target_user.user_name} from a different organization is not allowed.")