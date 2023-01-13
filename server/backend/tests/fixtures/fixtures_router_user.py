import logging

import pytest
import tests.router.disabled_test_router_user as test_router_user

LOGGER = logging.getLogger(__name__)
endPoint = test_router_user.endPoint


@pytest.fixture(scope="function")
def user_client_withUsersNoCleanup(
    test_client_fixture, user_data_dict, dbsession_fam_user_types
):
    # used for delete, assumption is the test user that was created
    # has been cleaned up.
    user_data_dict["create_date"] = str(user_data_dict["create_date"])
    user_data_dict["update_date"] = str(user_data_dict["update_date"])

    resp = test_client_fixture.post(f"{endPoint}", json=user_data_dict)
    LOGGER.debug(f"setup user table with data: {resp.status_code} " + f"{resp.reason}")
    LOGGER.debug(f"setup user table with data: {resp.status_code} " + f"{resp.reason}")
    LOGGER.debug(f"setup data: {user_data_dict}")
    if resp.status_code != 200:
        raise ValueError(
            "should work! but... can't create this record: " +
            f" {user_data_dict}, the response is: {resp.reason}"
        )
    return test_client_fixture


@pytest.fixture(scope="function")
def user_client_withUsers(test_client_fixture, user_data_dict, dbsession_fam_user_types):
    user_data_dict["create_date"] = str(user_data_dict["create_date"])
    user_data_dict["update_date"] = str(user_data_dict["update_date"])

    resp = test_client_fixture.post(f"{endPoint}", json=user_data_dict)
    LOGGER.debug(f"setup user table with data: {resp.status_code}" + f"  {resp.reason}")
    if resp.status_code != 200:
        raise ValueError(
            "should work! but... can't create this record: " +
            f" {user_data_dict}, the response is: {resp.reason}"
        )
    yield test_client_fixture

    respData = resp.json()

    LOGGER.debug(f"delete result: {respData}")
    resp = test_client_fixture.delete(f"{endPoint}/{respData['user_id']}")
    LOGGER.debug(
        "status code from removing user_id: " +
        f"{respData['user_id']} {resp.status_code}"
    )
