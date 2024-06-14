import logging
import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from api.app.crud import crud_user_terms_conditions
from testspg.constants import TEST_USER_ID, TEST_CREATOR


LOGGER = logging.getLogger(__name__)
TERMS_CONSITIONS_VERSION = "1"
ERROR_DUPLICATION = "User already accepted terms and conditions."


def test_get_user_terms_conditions_by_user_id_and_version(db_pg_session: Session):
    # verify test user has no record in terms conditions table
    assert (
        crud_user_terms_conditions.get_user_terms_conditions_by_user_id_and_version(
            db_pg_session, TEST_USER_ID, TERMS_CONSITIONS_VERSION
        )
        is None
    )

    # create user terms and conditions acceptance record
    crud_user_terms_conditions.create_user_terms_conditions(
        db_pg_session, TEST_USER_ID, TERMS_CONSITIONS_VERSION, TEST_CREATOR
    )

    # verify the user terms conditions record is created
    fam_user_temrs_conditions = (
        crud_user_terms_conditions.get_user_terms_conditions_by_user_id_and_version(
            db_pg_session, TEST_USER_ID, TERMS_CONSITIONS_VERSION
        )
    )
    assert fam_user_temrs_conditions is not None
    assert fam_user_temrs_conditions.user_id == TEST_USER_ID


def test_create_user_terms_conditions(db_pg_session: Session):
    # creating user terms conditions record for business bceid delegated admin is tested in test_require_accept_terms_and_conditions

    # create user terms and conditions acceptance record
    new_fam_user_temrs_conditions = (
        crud_user_terms_conditions.create_user_terms_conditions(
            db_pg_session, TEST_USER_ID, TERMS_CONSITIONS_VERSION, TEST_CREATOR
        )
    )
    # verify the user terms conditions record is created
    fam_user_temrs_conditions = (
        crud_user_terms_conditions.get_user_terms_conditions_by_user_id_and_version(
            db_pg_session, TEST_USER_ID, TERMS_CONSITIONS_VERSION
        )
    )
    assert (
        fam_user_temrs_conditions.user_terms_conditions_id
        == new_fam_user_temrs_conditions.user_terms_conditions_id
    )
    assert fam_user_temrs_conditions.user_id == new_fam_user_temrs_conditions.user_id

    # create duplicate user terms condtidions acceptance record will raise error
    with pytest.raises(HTTPException) as e:
        crud_user_terms_conditions.create_user_terms_conditions(
            db_pg_session, TEST_USER_ID, TERMS_CONSITIONS_VERSION, TEST_CREATOR
        )
    assert str(e._excinfo).find(ERROR_DUPLICATION) != -1
