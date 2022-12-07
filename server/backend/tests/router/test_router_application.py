import datetime
import logging
import starlette.testclient
from typing import Dict, Union, TypedDict
from api.app.main import apiPrefix

LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/fam_applications"


class ClientAndAppID(TypedDict):
    client: starlette.testclient.TestClient
    app_id: int


def test_get_fam_application_nodata(
    test_client_fixture: starlette.testclient.TestClient,
):
    response = test_client_fixture.get(f"{endPoint}")
    LOGGER.debug(f"endPoint: {endPoint}")
    LOGGER.debug(f"response {response}")
    assert response.status_code == 204
    data = response.json()
    LOGGER.debug(f"data: {data}")
    assert data == []


def test_get_fam_application(
    client_application: starlette.testclient.TestClient,
    application_dict: Dict[str, Union[str, datetime.datetime]],
):
    response = client_application.get(f"{endPoint}/")
    LOGGER.debug(f"response: {response}")
    data = response.json()
    LOGGER.debug(f"data: {data}")
    assert len(data) == 1
    assert data[0]["application_name"] == application_dict["application_name"]


def test_delete_fam_application(
    client_application: starlette.testclient.TestClient,
    application_dict: Dict[str, Union[str, datetime.datetime]],
):
    # verfiy that a record is being returned, so we have something to
    # be deleted
    response = client_application.get(f"{endPoint}/")
    LOGGER.debug(f"response: {response}")
    data = response.json()
    assert len(data) == 1

    LOGGER.debug(f"data: {data}")

    app_id = data[0]["application_id"]
    delete_end_point = f"{endPoint}/{app_id}"
    response = client_application.delete(delete_end_point)
    LOGGER.debug(f"response: {response.status_code}")

    # now verify that there are no application records
    get_resp = client_application.get(f"{endPoint}/")
    get_data = get_resp.json()
    assert get_resp.status_code == 204
    assert get_data == []


def test_post_fam_application(
    test_client_fixture: starlette.testclient.TestClient,
    application_dict: Dict[str, Union[str, datetime.datetime]],
):
    LOGGER.debug(f"application_dict: {application_dict}")
    application_dict["create_date"] = str(application_dict["create_date"])
    application_dict["update_date"] = str(application_dict["update_date"])
    post_resp = test_client_fixture.post(f"{endPoint}", json=application_dict)
    LOGGER.debug(f"resp status: {post_resp.status_code}")
    assert post_resp.status_code == 200

    # make sure that there is data in the application
    get_resp = test_client_fixture.get(f"{endPoint}")
    get_data = get_resp.json()
    record_added = False
    test_record = None
    for record in get_data:
        LOGGER.debug(f"data: record: {record}")
        LOGGER.debug(f"application_dict: {application_dict}")
        if application_dict["application_name"] == record["application_name"]:
            record_added = True
            test_record = record
    assert record_added

    # cleanup after test
    delete_end_point = f"{endPoint}/{test_record['application_id']}"
    delete_response = test_client_fixture.delete(delete_end_point)
    assert delete_response.status_code == 200


def test_get_fam_application_roles(
    application_roles: ClientAndAppID,
    application_dict: Dict[str, Union[str, datetime.datetime]],
    concrete_role_dict,
    concrete_role2_dict,
):
    client = application_roles["client"]
    app_id = application_roles["app_id"]
    # need to get the app id

    role_end_point = endPoint + f"/{app_id}/fam_roles"
    LOGGER.debug(f"role_end_point: {role_end_point}")
    resp = client.get(role_end_point)
    LOGGER.debug(f"resp status: {resp.status_code}")
    resp_data = resp.json()
    LOGGER.debug(f"resp data as JSON: {resp.text}")
    LOGGER.debug(f"resp data as dict: {resp_data}")

    role_data = {}
    for return_role in resp_data:
        role_data[return_role["role_name"]] = return_role
    # organize into a dict with key as role_name

    role_name = concrete_role_dict["role_name"]
    return_role = role_data[role_name]
    assert return_role["role_purpose"] == concrete_role_dict["role_purpose"]
    assert return_role["role_purpose"] == concrete_role_dict["role_purpose"]
    assert return_role["application_id"] == app_id

    role_name = concrete_role2_dict["role_name"]
    return_role = role_data[role_name]
    assert return_role["role_purpose"] == concrete_role2_dict["role_purpose"]
    assert return_role["role_purpose"] == concrete_role2_dict["role_purpose"]
    assert return_role["application_id"] == app_id


def test_get_fam_user_role_assignment(
    application_role_assignment,
    application_dict,
    concrete_role_dict,
    concrete_role2_dict,
    abstract_role_data,
    user_data_dict,
):

    client = application_role_assignment["client"]
    app_id = application_role_assignment["app_id"]

    role_end_point = endPoint + f"/{app_id}/user_role_assignment"
    resp = client.get(role_end_point)
    role_assignments = resp.json()
    LOGGER.debug(f"resp data: {role_assignments}")
    LOGGER.debug(f"json str: {resp.text}")

    # assert that there are 2 returned objects
    assert len(role_assignments) == 2

    role_names = []
    # getting the role names
    for assignment in role_assignments:
        role_names.append(assignment["role"]["role_name"])

    assert concrete_role_dict["role_name"] in role_names
    assert concrete_role2_dict["role_name"] in role_names
    assert abstract_role_data["role_name"] not in role_names

    # assert the user that is assigned to the two roles is the correct user
    user_properties_2_check = ["user_type_code", "cognito_user_id", "user_name"]
    for assignment in role_assignments:
        for property_to_check in user_properties_2_check:
            assert (
                assignment["user"][property_to_check]
                == user_data_dict[property_to_check]
            )
