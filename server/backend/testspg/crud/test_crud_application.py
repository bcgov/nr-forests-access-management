import logging

from api.app.crud import crud_application
from sqlalchemy.orm import Session
from testspg.constants import NOT_EXIST_APPLICATION_ID


LOGGER = logging.getLogger(__name__)

TEST_APPLICATION_NAME_NOT_FOUND = "NOT_FOUND"
TEST_APPLICATION_NAME_FAM = "FAM"
TEST_APPLICATION_ID_FAM = 1


def test_get_application(db_pg_session: Session):
    app_by_id = crud_application.get_application(
        db=db_pg_session, application_id=TEST_APPLICATION_ID_FAM
    )
    assert app_by_id.application_id == TEST_APPLICATION_ID_FAM
    assert app_by_id.application_name == TEST_APPLICATION_NAME_FAM

    app_by_id = crud_application.get_application(
        db=db_pg_session, application_id=NOT_EXIST_APPLICATION_ID
    )
    assert app_by_id is None
