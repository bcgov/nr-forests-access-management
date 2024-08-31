from api.app.constants import UserType
from api.app.models import FamUserModel
from api.app.routers import router_guards
from sqlalchemy import insert
from sqlalchemy.orm import Session
from testspg.constants import TEST_CREATOR, USER_NAME_BCEID_LOAD_2_TEST
from testspg.jwt_utils import COGNITO_USERNAME_BCEID_DELEGATED_ADMIN


def test_get_current_requester_contains_is_delegated_admin(db_pg_session: Session):
    """
    Test the `get_current_requester` function result:
    * when user is a delegated admin => is_delegated_admin: True
    * when user is not a delegated admin => is_delegated_admin: False
    """
    # as not a delegated admin
    cognito_user_id = "not_delegated_admin_cognito_user_id"
    db_pg_session.execute(
        insert(FamUserModel),
        [
            {
                "user_type_code": UserType.BCEID,
                "user_name": USER_NAME_BCEID_LOAD_2_TEST,
                "user_guid": "_test_dummy_user_guid_32_length_",
                "cognito_user_id": cognito_user_id,
                "create_user": TEST_CREATOR,
            }
        ],
    )
    requester = router_guards.get_current_requester(
        request_cognito_user_id=cognito_user_id,
        access_roles=["dummy", "role"],
        db=db_pg_session,
    )
    assert requester.user_name == USER_NAME_BCEID_LOAD_2_TEST
    assert requester.is_delegated_admin is False

    # as a delegated admin
    requester = router_guards.get_current_requester(
        request_cognito_user_id=COGNITO_USERNAME_BCEID_DELEGATED_ADMIN,
        access_roles=["dummy", "role"],
        db=db_pg_session,
    )
    assert requester.cognito_user_id == COGNITO_USERNAME_BCEID_DELEGATED_ADMIN
    assert requester.is_delegated_admin is True
