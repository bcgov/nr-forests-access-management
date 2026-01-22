"""
Test data and helper functions for user role assignment CRUD tests.
"""
from typing import List, Optional
from api.app.schemas import RequesterSchema, TargetUserSchema
from api.app.schemas.fam_user_role_assignment_create import FamUserRoleAssignmentCreateSchema, FamUserRoleAssignmentUserSchema
from api.app.constants import UserType
from testspg.constants import TEST_REQUESTER


def create_role_assignment_request(
    users: List[TargetUserSchema],
    user_type_code: UserType,
    role_id: int,
    forest_client_numbers: Optional[List[str]] = None,
    requires_send_user_email: bool = False,
    expiry_date_date: Optional[str] = None
) -> FamUserRoleAssignmentCreateSchema:
    """
    Helper function to create FamUserRoleAssignmentCreateSchema for testing.

    :param users: List of target users
    :param user_type_code: User type code (IDIR, BCEID, etc.)
    :param role_id: Role ID to assign
    :param forest_client_numbers: Optional list of forest client numbers
    :param requires_send_user_email: Whether to send email notifications
    :param expiry_date_date: Optional expiry date in YYYY-MM-DD format
    :return: FamUserRoleAssignmentCreateSchema instance
    """
    user_list = [
        FamUserRoleAssignmentUserSchema(
            user_name=user.user_name,
            user_guid=user.user_guid
        )
        for user in users
    ]

    return FamUserRoleAssignmentCreateSchema(
        users=user_list,
        user_type_code=user_type_code,
        role_id=role_id,
        forest_client_numbers=forest_client_numbers,
        requires_send_user_email=requires_send_user_email,
        expiry_date_date=expiry_date_date
    )


def create_test_requester() -> RequesterSchema:
    """
    Helper function to create RequesterSchema for testing.

    :return: RequesterSchema instance with test data
    """
    return RequesterSchema(**TEST_REQUESTER)
