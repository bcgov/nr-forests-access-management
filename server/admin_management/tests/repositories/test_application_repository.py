import logging

from api.app.repositories.application_repository import ApplicationRepository

from tests.constants import (
    TEST_NOT_EXIST_APPLICATION_ID,
    TEST_APPLICATION_ID_FAM,
    TEST_APPLICATION_NAME_FAM,
)


LOGGER = logging.getLogger(__name__)


def test_get_application(application_repo: ApplicationRepository):
    # test get existing application
    app_by_id = application_repo.get_application(TEST_APPLICATION_ID_FAM)
    assert app_by_id.application_id == TEST_APPLICATION_ID_FAM
    assert app_by_id.application_name == TEST_APPLICATION_NAME_FAM

    # test get non exist application
    app_by_id = application_repo.get_application(TEST_NOT_EXIST_APPLICATION_ID)
    assert app_by_id is None
