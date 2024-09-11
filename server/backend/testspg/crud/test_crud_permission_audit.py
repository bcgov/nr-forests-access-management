import pytest
from sqlalchemy.orm import Session
from api.app.crud.crud_permission_audit import (
    read_permission_audit_history_by_user_and_application,
)
from testspg.fixture.permission_audit_fixture import (
    APPLICATION_ID_1,
    AUDIT_RECORD_1,
    AUDIT_RECORD_2,
    AUDIT_RECORD_3,
    CHANGE_DATE_1,
    CHANGE_DATE_2,
    USER_ID_1,
)

# No Records
def test_read_permission_audit_history_no_records(db_pg_session: Session):
    # Ensure the database has no matching records
    user_id = 999
    application_id = 999

    result = read_permission_audit_history_by_user_and_application(
        user_id, application_id, db_pg_session
    )

    # Ensure the result is an empty list
    assert len(result) == 0

# No Matching Records
def test_read_permission_audit_history_no_matching_records(db_pg_session: Session):
    # Ensure no records exist for specific user/application
    user_id = 999
    application_id = 999

    result = read_permission_audit_history_by_user_and_application(
        user_id, application_id, db_pg_session
    )

    # Ensure the result is an empty list
    assert result == []

# Invalid Data Types
def test_read_permission_audit_history_invalid_data_types(db_pg_session: Session):
    with pytest.raises(ValueError):
        read_permission_audit_history_by_user_and_application(
            "invalid_user_id", APPLICATION_ID_1, db_pg_session
        )

# Multiple Users, Same Application
def test_read_permission_audit_history_multiple_users_same_application(db_pg_session: Session):
    # Add records for two different users but the same application
    db_pg_session.add(AUDIT_RECORD_1)
    db_pg_session.add(AUDIT_RECORD_2)
    db_pg_session.commit()

    result = read_permission_audit_history_by_user_and_application(
        USER_ID_1, APPLICATION_ID_1, db_pg_session
    )

    # Ensure only USER_ID_1's record is returned
    assert len(result) == 1
    assert result[0].change_target_user_id == USER_ID_1
    assert result[0].change_performer_user_details["username"] == "bigfoot_hunter"

# Multiple Applications, Same User
def test_read_permission_audit_history_multiple_applications_same_user(db_pg_session: Session):
    # Add records for the same user but different applications
    db_pg_session.add(AUDIT_RECORD_1)
    db_pg_session.add(AUDIT_RECORD_3)
    db_pg_session.commit()

    result = read_permission_audit_history_by_user_and_application(
        USER_ID_1, APPLICATION_ID_1, db_pg_session
    )

    # Ensure only APPLICATION_ID_1's record is returned
    assert len(result) == 1
    assert result[0].application_id == APPLICATION_ID_1
    assert result[0].change_performer_user_details["username"] == "bigfoot_hunter"

# Valid Case
def test_read_permission_audit_history_by_user_and_application(db_pg_session: Session):
    # Add records to the database
    db_pg_session.add(AUDIT_RECORD_1)
    db_pg_session.add(AUDIT_RECORD_2)
    db_pg_session.commit()

    result = read_permission_audit_history_by_user_and_application(
        USER_ID_1, APPLICATION_ID_1, db_pg_session
    )

    # Ensure two records are returned in the correct order
    assert len(result) == 2
    assert result[0].change_date == CHANGE_DATE_2  # Newest first
    assert result[1].change_date == CHANGE_DATE_1  # Oldest last
