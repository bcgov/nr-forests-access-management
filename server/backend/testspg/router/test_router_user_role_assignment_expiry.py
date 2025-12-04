import datetime
from datetime import timedelta
from http import HTTPStatus
from zoneinfo import ZoneInfo

from api.app.datetime_format import BC_TIMEZONE, DATE_FORMAT_YYYY_MM_DD
from api.app.main import internal_api_prefix
from fastapi.testclient import TestClient
from testspg import jwt_utils
from testspg.constants import ACCESS_GRANT_FOM_DEV_CR_IDIR

BC_TZ = ZoneInfo(BC_TIMEZONE)

endPoint = f"{internal_api_prefix}/user-role-assignment"

def test_create_user_role_assignment_with_future_expiry_date(
    test_client_fixture: TestClient,
    db_pg_session,
    fom_dev_access_admin_token,
    override_depends__get_verified_target_user
):
    """
    Test assigning a role with an expiry date.
    """
    future_date = (datetime.datetime.now(BC_TZ) + datetime.timedelta(days=30)).date()
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
        expiry_date_str.endswith("T07:59:59+00:00")
        or expiry_date_str.endswith("T06:59:59+00:00")
        or expiry_date_str.endswith("T07:59:59Z")
        or expiry_date_str.endswith("T06:59:59Z")
    )
    # Expect expiry string to start with the day after future_date
    utc_day = future_date + timedelta(days=1)
    assert expiry_date_str.startswith(utc_day.strftime(DATE_FORMAT_YYYY_MM_DD))

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
    past_date = (datetime.datetime.now(BC_TZ) - datetime.timedelta(days=1)).date()
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
    invalid_date = (datetime.datetime.now(BC_TZ) + datetime.timedelta(days=30)).strftime("%d-%m-%Y")
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


def test_create_user_role_assignment_with_today_as_expiry_date(
    test_client_fixture: TestClient,
    fom_dev_access_admin_token,
    override_depends__get_verified_target_user,
):
    """
    Test assigning a role with expiry date as today (should be accepted, valid until midnight BC time).
    """
    BC_TODAY = datetime.datetime.now(BC_TZ).date()
    request_data = {
        **ACCESS_GRANT_FOM_DEV_CR_IDIR,
        "expiry_date_date": BC_TODAY.strftime(DATE_FORMAT_YYYY_MM_DD),
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
    # Check expiry is today at 23:59:59 BC time (UTC)
    expiry_date_str = detail["expiry_date"]
    assert isinstance(expiry_date_str, str)
    # The UTC date will be the next day at 07:59:59+00:00 or 06:59:59+00:00 depending on DST
    utc_day = BC_TODAY + timedelta(days=1)
    assert (
        expiry_date_str.startswith(utc_day.strftime(DATE_FORMAT_YYYY_MM_DD))
        and (
            expiry_date_str.endswith("T07:59:59+00:00")
            or expiry_date_str.endswith("T06:59:59+00:00")
            or expiry_date_str.endswith("T07:59:59Z")
            or expiry_date_str.endswith("T06:59:59Z")
        )
    )


def test_create_user_role_assignment_with_tomorrow_just_before_midnight(
    test_client_fixture: TestClient,
    fom_dev_access_admin_token,
    override_depends__get_verified_target_user,
):
    """
    Test assigning a role with expiry date as tomorrow (should be accepted).
    """
    tomorrow = (datetime.datetime.now(BC_TZ) + datetime.timedelta(days=1)).date()
    request_data = {
        **ACCESS_GRANT_FOM_DEV_CR_IDIR,
        "expiry_date_date": tomorrow.strftime(DATE_FORMAT_YYYY_MM_DD),
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
    assert detail["expiry_date"] is not None


def test_create_user_role_assignment_with_leap_year_expiry_date(
    test_client_fixture: TestClient,
    fom_dev_access_admin_token,
    override_depends__get_verified_target_user,
):
    """
    Test assigning a role with expiry date as February 29 on a leap year (should be accepted if valid).
    """
    # Find the next leap year
    year = datetime.datetime.now(BC_TZ).year
    while True:
        if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)):
            feb_29 = datetime.date(year, 2, 29)
            if feb_29 > datetime.datetime.now(BC_TZ).date():
                break
        year += 1
    request_data = {
        **ACCESS_GRANT_FOM_DEV_CR_IDIR,
        "expiry_date_date": feb_29.strftime(DATE_FORMAT_YYYY_MM_DD),
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
    assert detail["expiry_date"] is not None


def test_create_user_role_assignment_with_expiry_date_near_dst_change(
    test_client_fixture: TestClient,
    fom_dev_access_admin_token,
    override_depends__get_verified_target_user,
):
    """
    Test assigning a role with expiry date near a daylight saving time change (ensure BC timezone is always used, and no off-by-one-hour errors).
    """
    # Use a known DST change date for BC (e.g., second Sunday in March or first Sunday in November)
    # We'll use the next DST start (March) or end (November) after today
    today = datetime.datetime.now(BC_TZ).date()
    year = today.year
    # DST starts: second Sunday in March
    march = datetime.date(year, 3, 1)
    first_sunday = march + datetime.timedelta(days=(6 - march.weekday()) % 7)
    second_sunday = first_sunday + datetime.timedelta(days=7)
    dst_date = second_sunday
    if dst_date <= today:
        # If already passed, use next year
        year += 1
        march = datetime.date(year, 3, 1)
        first_sunday = march + datetime.timedelta(days=(6 - march.weekday()) % 7)
        second_sunday = first_sunday + datetime.timedelta(days=7)
        dst_date = second_sunday
    request_data = {
        **ACCESS_GRANT_FOM_DEV_CR_IDIR,
        "expiry_date_date": dst_date.strftime(DATE_FORMAT_YYYY_MM_DD),
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
    assert detail["expiry_date"] is not None


def test_create_user_role_assignment_with_far_future_expiry_date(
    test_client_fixture: TestClient,
    fom_dev_access_admin_token,
    override_depends__get_verified_target_user,
):
    """
    Test assigning a role with expiry date many years in the future (should be accepted if within allowed range).
    """
    far_future = (datetime.datetime.now(BC_TZ) + datetime.timedelta(days=365 * 20)).date()
    request_data = {
        **ACCESS_GRANT_FOM_DEV_CR_IDIR,
        "expiry_date_date": far_future.strftime(DATE_FORMAT_YYYY_MM_DD),
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
    assert detail["expiry_date"] is not None


def test_create_user_role_assignment_with_empty_string_expiry_date(
    test_client_fixture: TestClient,
    fom_dev_access_admin_token,
    override_depends__get_verified_target_user,
):
    """
    Test assigning a role with expiry date as an empty string (should be treated as no expiry).
    """
    request_data = {
        **ACCESS_GRANT_FOM_DEV_CR_IDIR,
        "expiry_date_date": "",
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
    assert detail["expiry_date"] is None


def test_create_user_role_assignment_with_null_expiry_date(
    test_client_fixture: TestClient,
    fom_dev_access_admin_token,
    override_depends__get_verified_target_user,
):
    """
    Test assigning a role with expiry date as null (should be treated as no expiry).
    """
    request_data = {
        **ACCESS_GRANT_FOM_DEV_CR_IDIR,
        "expiry_date_date": None,
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
    assert detail["expiry_date"] is None
