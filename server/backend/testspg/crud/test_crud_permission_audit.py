import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import DataError
from api.app.crud.crud_permission_audit import (
    read_permission_audit_history_by_user_and_application,
)
from testspg.fixture.permission_audit_fixture import (
    APPLICATION_ID_1,
    APPLICATION_ID_2,
    AUDIT_RECORD_U1_A1_D1,
    AUDIT_RECORD_U1_A1_D2,
    AUDIT_RECORD_U1_A2,
    AUDIT_RECORD_U2_A2,
    USER_ID_1,
    PERFORMER_DETAILS_1,
)


# No Records
def test_read_permission_audit_history_no_records(db_pg_session: Session):
    user_id = 999
    application_id = 999

    result = read_permission_audit_history_by_user_and_application(
        user_id, application_id, db_pg_session
    )

    assert len(result) == 0


# No Matching Records
def test_read_permission_audit_history_no_matching_records(db_pg_session: Session):
    user_id = 999
    application_id = 999

    result = read_permission_audit_history_by_user_and_application(
        user_id, application_id, db_pg_session
    )

    assert result == []


# Invalid Data Types
def test_read_permission_audit_history_invalid_data_types(db_pg_session: Session):
    with pytest.raises(DataError):
        read_permission_audit_history_by_user_and_application(
            "invalid_user_id", APPLICATION_ID_1, db_pg_session
        )


# Multiple Users, Same Application
def test_read_permission_audit_history_multiple_users_same_application(
    db_pg_session: Session,
):
    db_pg_session.add(AUDIT_RECORD_U1_A2)
    db_pg_session.add(AUDIT_RECORD_U2_A2)

    result = read_permission_audit_history_by_user_and_application(
        USER_ID_1, APPLICATION_ID_2, db_pg_session
    )

    assert len(result) == 1
    assert (
        result[0].change_performer_user_id
        == AUDIT_RECORD_U1_A2.change_performer_user_id
    )
    assert (
        result[0].change_performer_user_details.username
        == PERFORMER_DETAILS_1["username"]
    )


# Multiple Applications, Same User
def test_read_permission_audit_history_multiple_applications_same_user(
    db_pg_session: Session,
):
    db_pg_session.add(AUDIT_RECORD_U1_A2)
    db_pg_session.add(AUDIT_RECORD_U1_A1_D1)

    result = read_permission_audit_history_by_user_and_application(
        USER_ID_1, APPLICATION_ID_1, db_pg_session
    )

    assert len(result) == 1
    assert (
        result[0].change_performer_user_id
        == AUDIT_RECORD_U1_A1_D1.change_performer_user_id
    )
    assert (
        result[0].change_performer_user_details.username
        == PERFORMER_DETAILS_1["username"]
    )


# Valid Case
def test_read_permission_audit_history_by_user_and_application(db_pg_session: Session):
    db_pg_session.add(AUDIT_RECORD_U1_A1_D1)
    db_pg_session.add(AUDIT_RECORD_U1_A1_D2)

    result = read_permission_audit_history_by_user_and_application(
        USER_ID_1, APPLICATION_ID_1, db_pg_session
    )

    assert len(result) == 2
    assert result[0].change_date == AUDIT_RECORD_U1_A1_D2.change_date  # Newest first
    assert result[1].change_date == AUDIT_RECORD_U1_A1_D1.change_date  # Oldest last
