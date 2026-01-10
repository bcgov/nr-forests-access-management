from api.app.schemas import RequesterSchema, TargetUserSchema
from api.app.schemas.target_user_validation_result import TargetUserValidationResultSchema
from api.app.models.model import FamRole
from api.app.crud import crud_utils
from api.app.crud.validator.target_user_validator import TargetUserValidator
import logging

LOGGER = logging.getLogger(__name__)

def validate_verified_target_users(
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
            LOGGER.warning(f"User validation failed for {target_user.user_name}: {e}")
            failed_users.append(target_user)
    return TargetUserValidationResultSchema(verified_users=verified_users, failed_users=failed_users)
