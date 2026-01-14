
from typing import List, Tuple
from api.app import constants as famConstants
from api.app.utils.utils import raise_http_exception
from api.app.schemas.fam_user_role_assignment_create import FamUserRoleAssignmentCreateSchema
from api.app.schemas.requester import RequesterSchema
from api.app.schemas.target_user import TargetUserSchema
from api.app.crud.validator.target_user_validator import validate_bceid_same_org

def validate_request_type(request: FamUserRoleAssignmentCreateSchema) -> bool:
	"""
	Granting user role assignment method's validator.
	Validate that the request user_type_code is supported for (IDIR or BCEID).
	Returns:
		bool: True if valid, False otherwise.
	"""
	return request.user_type_code in (famConstants.UserType.IDIR, famConstants.UserType.BCEID)


def validate_bceid_same_org_users(
	requester: RequesterSchema,
	users: List[TargetUserSchema],
	user_type_code: famConstants.UserType,
) -> Tuple[List[TargetUserSchema], List[Tuple[TargetUserSchema, str]]]:
	"""
	Granting user role assignment method's helper validator.
	Validate BCeID requester can only grant BCeID users for same-organization constraint.

	Parameters:
		requester (RequesterSchema): The user making the request.
		users (List[TargetUserSchema]): List of users to validate.
		user_type_code (str): The requested user grant user type code (IDIR or BCEID).

	Returns:
		Tuple[List[TargetUserSchema], List[Tuple[TargetUserSchema, str]]]:
			- valid_users: Users passing same-org validation.
			- failed_users: List of (user, error_reason) for failed users.
	"""
	if user_type_code == famConstants.UserType.BCEID:
		valid_users = []
		failed_users = []
		for user in users:
			try:
				validate_bceid_same_org(requester, user)
				valid_users.append(user)
			except Exception as e:
				failed_users.append((user, str(e)))
		return valid_users, failed_users
	else:
		return users, []

