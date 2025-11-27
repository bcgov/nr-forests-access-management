import datetime
from http import HTTPStatus

from api.app.datetime_format import DATE_FORMAT_YYYY_MM_DD
from api.app.main import internal_api_prefix
from fastapi.testclient import TestClient
from testspg import jwt_utils
from testspg.constants import ACCESS_GRANT_FOM_DEV_CR_IDIR

endPoint = f"{internal_api_prefix}/user-role-assignment"

def test_create_user_role_assignment_with_future_expiry_date(
    test_client_fixture: TestClient,
    db_pg_session,
    fom_dev_access_admin_token,
    get_current_requester_by_token,
    override_depends__get_verified_target_user,
    default_app_role_assignment_page_Params
):
    """
    Test assigning a role with an expiry date.
    """
    future_date = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)).date()
    request_data = {
        **ACCESS_GRANT_FOM_DEV_CR_IDIR,
        "expiry_date_date": future_date.strftime(DATE_FORMAT_YYYY_MM_DD),
    }
    override_depends__get_verified_target_user()
    response = test_client_fixture.post(
        endPoint,
        json=request_data,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json().get("assignments_detail")
    assert len(data) == 1
    detail = data[0]["detail"]
    assert "user_role_xref_id" in detail
    assert detail["expiry_date"] is not None
    application_id = detail["role"]["application"]["application_id"]
    get_response = test_client_fixture.get(
        f"{internal_api_prefix}/fam-applications/{application_id}/user-role-assignment",
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert get_response.status_code == HTTPStatus.OK
    get_data = get_response.json().get("results")
    found = [item for item in get_data if item["user_role_xref_id"] == detail["user_role_xref_id"]]
    assert len(found) == 1
    expiry_date_str = found[0]["expiry_date"]
    assert isinstance(expiry_date_str, str)
    assert (
        expiry_date_str.endswith("T08:00:00+00:00")
        or expiry_date_str.endswith("T07:00:00+00:00")
        or expiry_date_str.endswith("T08:00:00Z")
        or expiry_date_str.endswith("T07:00:00Z")
    )
    assert expiry_date_str.startswith(future_date.strftime(DATE_FORMAT_YYYY_MM_DD))

def test_create_user_role_assignment_without_expiry_date(
    test_client_fixture: TestClient,
    db_pg_session,
    fom_dev_access_admin_token,
    get_current_requester_by_token,
    override_depends__get_verified_target_user,
    default_app_role_assignment_page_Params
):
    """
    Test assigning a role without expiry date.
    """
    request_data = {
        **ACCESS_GRANT_FOM_DEV_CR_IDIR,
    }
    override_depends__get_verified_target_user()
    response = test_client_fixture.post(
        endPoint,
        json=request_data,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code == HTTPStatus.OK
    data = response.json().get("assignments_detail")
    assert len(data) == 1
    detail = data[0]["detail"]
    assert "user_role_xref_id" in detail
    assert detail["expiry_date"] is None
    application_id = detail["role"]["application"]["application_id"]
    get_response = test_client_fixture.get(
        f"{internal_api_prefix}/fam-applications/{application_id}/user-role-assignment",
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert get_response.status_code == HTTPStatus.OK
    get_data = get_response.json().get("results")
    found = [item for item in get_data if item["user_role_xref_id"] == detail["user_role_xref_id"]]
    assert len(found) == 1
    assert found[0]["expiry_date"] is None

def test_create_user_role_assignment_with_past_expiry_date(
    test_client_fixture: TestClient,
    fom_dev_access_admin_token,
    override_depends__get_verified_target_user,
):
    """
    Test assigning a role with a past expiry date (should fail validation).
    """
    past_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)).date()
    request_data = {
        **ACCESS_GRANT_FOM_DEV_CR_IDIR,
        "expiry_date_date": past_date.strftime(DATE_FORMAT_YYYY_MM_DD),
    }
    override_depends__get_verified_target_user()
    response = test_client_fixture.post(
        endPoint,
        json=request_data,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code in (HTTPStatus.UNPROCESSABLE_ENTITY, HTTPStatus.BAD_REQUEST)


def test_create_user_role_assignment_with_invalid_expiry_date_format(
    test_client_fixture: TestClient,
    fom_dev_access_admin_token,
    override_depends__get_verified_target_user,
):
    """
    Test assigning a role with an invalid expiry date format (should fail validation).
    """
    invalid_date = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)).strftime("%d-%m-%Y")
    request_data = {
        **ACCESS_GRANT_FOM_DEV_CR_IDIR,
        "expiry_date_date": invalid_date,
    }
    override_depends__get_verified_target_user()
    response = test_client_fixture.post(
        endPoint,
        json=request_data,
        headers=jwt_utils.headers(fom_dev_access_admin_token),
    )
    assert response.status_code in (HTTPStatus.UNPROCESSABLE_ENTITY, HTTPStatus.BAD_REQUEST)
