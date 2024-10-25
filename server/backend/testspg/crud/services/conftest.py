
import logging
import random

import pytest
from api.app.constants import UserType
from api.app.models.model import FamUser
from sqlalchemy.orm import Session
from testspg.constants import (BUSINESS_GUID_BCEID_LOAD_2_TEST,
                               BUSINESS_GUID_BCEID_LOAD_3_TEST)

LOGGER = logging.getLogger(__name__)

@pytest.fixture(scope="function")
def load_test_users(db_pg_session: Session):
    """
    This seeds fix amount of users into test db session. It might be only suitable
    for some test cases that need to prepare and test on some amount of users.
    At the end of the test function, user records will be rollback by db_pg_session.

    return: array of FamUser model contains 20 IDIR users and 125 BCEID users.
    """
    session = db_pg_session
    length_of_string = 4
    sample_str = "ABCDEFGH"

    idir_users = []
    for i in range(20):
        random_string = ''.join(random.choices(sample_str, k = length_of_string))
        idir_users.append(
            FamUser(
                user_type_code=UserType.IDIR, user_name=f"TEST_USER_IDIR_{i}", create_user="system_tester",
                first_name=f"First_Name_{i}", last_name=f"Last_Name_{i}", email=f"email_{i}_{random_string}@fam.test.com"
            )
        )

    bceid_users = []
    for i in range(125):
        random_string = ''.join(random.choices(sample_str, k = length_of_string))
        bceid_users.append(
            FamUser(
                user_type_code=UserType.BCEID, user_name=f"TEST_USER_BCEID_{i}", create_user="system_tester",
                first_name=f"First_Name_{i}", last_name=f"Last_Name_{i}", email=f"email_{i}_{random_string}@fam.test.com",
                business_guid=f"{BUSINESS_GUID_BCEID_LOAD_3_TEST if i % 5 == 0 else BUSINESS_GUID_BCEID_LOAD_2_TEST}"
            )
        )
    users = idir_users + bceid_users
    session.add_all(users)
    return users
