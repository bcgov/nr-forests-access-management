
import logging
import random
from typing import List

import pytest
from api.app.constants import UserType
from api.app.models.model import (FamApplication, FamForestClient, FamRole,
                                  FamUser, FamUserRoleXref)
from sqlalchemy import Select
from sqlalchemy.orm import Session
from testspg.constants import (BUSINESS_GUID_BCEID_LOAD_2_TEST,
                               BUSINESS_GUID_BCEID_LOAD_3_TEST)

LOGGER = logging.getLogger(__name__)

TEST_APPLICATION_NAME = "APP_TEST"

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
    session.flush()
    return {"idir_users": idir_users, "bceid_users": bceid_users}

@pytest.fixture(scope="function")
def load_fom_dev_user_role_test_data(db_pg_session: Session, load_test_users):
    session = db_pg_session

    # get existing db FOM_DEV submitter/reviewer roles
    fom_dev_reviewer_role: FamRole = session.scalars(
        Select(FamRole).join(FamRole.application)
        .where(FamRole.role_name == "FOM_REVIEWER", FamApplication.application_name == "FOM_DEV")
    ).one()
    fom_dev_submitter_role: FamRole = session.scalars(
        Select(FamRole).join(FamRole.application)
        .where(FamRole.role_name == "FOM_SUBMITTER", FamApplication.application_name == "FOM_DEV")
    ).one()

    # -- add test user/role assignments
    idir_test_users = load_test_users["idir_users"]
    test_reviewer_user_roles = [
        FamUserRoleXref(
            user=user,
            role=fom_dev_reviewer_role,
            create_user="system_tester"
        ) for user in idir_test_users  # assign IDIR users: reviewer role
    ]
    session.add_all(test_reviewer_user_roles)

    # create some temporary testing forest client number (do not use them to validate)
    test_forest_clients = [
        FamForestClient(forest_client_number="99009901", create_user="system_tester"),
        FamForestClient(forest_client_number="99009902", create_user="system_tester"),
        FamForestClient(forest_client_number="99009903", create_user="system_tester"),
        FamForestClient(forest_client_number="99009904", create_user="system_tester"),
        FamForestClient(forest_client_number="99009905", create_user="system_tester"),
    ]
    session.add_all(test_forest_clients)

    # create some submitter roles associated with the above forest client numbers
    test_submiter_roles_with_client_number = [
        FamRole(role_name=f"test_submitter_{fc.forest_client_number}",
                role_purpose=f"Submitter role for test application scoped with forest client {fc.forest_client_number}",
                display_name="Submitter",
                application=fom_dev_submitter_role.application,
                client_number=fc,
                parent_role=fom_dev_submitter_role,
                create_user="system_tester",
                role_type_code="C"
        )
        for fc in test_forest_clients
    ]
    session.add_all(test_submiter_roles_with_client_number)

    bceid_test_users: List[FamUser] = load_test_users["bceid_users"]
    test_submitter_user_roles = [
        FamUserRoleXref(
            user=user,
            role=test_submiter_roles_with_client_number[user.user_id % len(test_submiter_roles_with_client_number)],
            create_user="system_tester"
        ) for user in bceid_test_users  # assign BCeID users: submitter role
    ]
    session.add_all(test_submitter_user_roles)

    session.flush()
    return {"reviewers": test_reviewer_user_roles, "submitters": test_submitter_user_roles}