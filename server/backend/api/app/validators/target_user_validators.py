from api.app.constants import UserType
from api.app.schemas import RequesterSchema, TargetUserSchema, FamRole
from api.app.schemas.target_user_validation_result import TargetUserValidationResultSchema, FailedTargetUserSchema
from api.app.models.model import FamRole
from api.app.crud import crud_utils
from api.app.crud.validator.target_user_validator import TargetUserValidator
import logging

LOGGER = logging.getLogger(__name__)

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
