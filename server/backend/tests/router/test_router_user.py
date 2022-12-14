import logging

import api.app.constants as famConstants
from api.app.main import apiPrefix

LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/fam_users"


def test_get_fam_users_nodata(test_client_fixture):
    response = test_client_fixture.get(f"{endPoint}/")
    LOGGER.debug(f"endPoint: {endPoint}")
    LOGGER.debug(f"response {response}")
    assert response.status_code == 200
    data = response.json()
    LOGGER.debug(f"data: {data}")
    assert data == []


def test_get_fam_users_withdata(user_client_withUsers):
    response = user_client_withUsers.get(f"{endPoint}")
    LOGGER.debug(f"response: {response}")
    data = response.json()
    LOGGER.debug(f"data: {data}")


def test_delete_fam_user(user_client_withUsersNoCleanup, test_client_fixture):
    response = user_client_withUsersNoCleanup.get(endPoint)
    LOGGER.debug(f"response: {response}")
    respData = response.json()
    LOGGER.debug(f"data: {respData}")
    # start of by making sure we have data
    assert len(respData) > 0 and "user_type_code" in respData[0]

    # delete the data
    respDelete = user_client_withUsersNoCleanup.delete(
        f"{endPoint}/{respData[0]['user_id']}"
    )
    LOGGER.debug(f"delete resp: {respDelete.reason}")
    assert respDelete.status_code == 200

    # double check that the record is missing from the data now
    # test_client_fixture.
    responseAD = test_client_fixture.get(endPoint)
    respDataADData = responseAD.json()
    for i in respDataADData:
        if i["user_id"] == respData[0]["user_id"]:
            LOGGER.debug("response data... record didnt get deleted: " +
                         f"{respData[0]}")
        assert i["user_id"] != respData[0]["user_id"]


def test_get_fam_user(user_client_withUsers):
    # retrieval of user is by id, don't know what id got
    # assigned so getting all the users, from that can
    # test the get individual user end point
    allUsersResponse = user_client_withUsers.get(f"{endPoint}")
    allUsersData = allUsersResponse.json()
    LOGGER.debug(f"user data: {allUsersData}")
    for user in allUsersData:
        singleUser = user_client_withUsers.get(f"{endPoint}/{user['user_id']}")
        singleUserData = singleUser.json()
        assert singleUserData == user


def test_post_fam_users(test_client_fixture, user_data_dict, dbsession_fam_user_types):

    # modify the user data to make it invalid
    user_data_dict["user_type_code"] = "X"
    user_data_dict['create_date'] = str(user_data_dict['create_date'])
    user_data_dict['update_date'] = str(user_data_dict['update_date'])

    resp = test_client_fixture.post(f"{endPoint}", json=user_data_dict)
    body = resp.json()
    LOGGER.debug(f"body: {body}")
    assert resp.status_code == 422
    expectedMessage = "value is not a valid enumeration member; permitted: 'I', 'B'"
    assert body['detail'][0]['msg'] == expectedMessage

    # fix the data so the post should succeed
    user_data_dict["user_type_code"] = famConstants.UserType.BCEID
    resp = test_client_fixture.post(f"{endPoint}", json=user_data_dict)
    respData = resp.json()
    LOGGER.debug(f"resp data: {resp.json()}")
    assert resp.status_code == 200

    # comment-out: being enforced yet in model.
    # verify that a record with the same 'guid' cannot be entered
    # respDataCopy = respData.copy()
    # del respDataCopy["user_id"]
    # resp = test_client_fixture.post(f"{endPoint}", json=respDataCopy)
    # respBody = resp.json()
    # LOGGER.debug(f"resp data: {resp.status_code} - {resp.json()}")
    # assert resp.status_code == 422
    # assert "IntegrityError" in respBody["detail"]

    # cleanup by deleting the user
    resp = test_client_fixture.delete(f"{endPoint}/{respData['user_id']}")
    data = resp.json()
    LOGGER.debug(f"result: {data} {resp.status_code}")
    # making sure the delete was successful, but not testing delete end point
    # here
    assert resp.status_code == 200
