import logging
from typing import Dict, Iterator, Union

import api.app.constants as famConstants
import api.app.models.model as model
import api.app.schemas as schemas
import pytest
from sqlalchemy import text
from sqlalchemy.orm import session

LOGGER = logging.getLogger(__name__)

FOM_SUBMITTER_ROLE_NAME = "FOM_Submitter"


@pytest.fixture(scope="function")
def user_role_dict() -> Iterator[Dict[str, Union[str, int]]]:
    user_role_data = {
        "user_name": "Test User",
        "user_type_code": famConstants.UserType.BCEID,
        "role_id": 2,
        "forest_client_number": "00001001",
    }
    yield user_role_data


@pytest.fixture(scope="function")
def user_role_assignment_model(user_role_dict) -> schemas.FamUserRoleAssignmentCreate:
    fam_user_role_request = schemas.FamUserRoleAssignmentCreate(**user_role_dict)
    yield fam_user_role_request


@pytest.fixture(scope="function")
def dbsession_user_role_assignment(
    request, dbsession_fam_user_types,
    dbsession_FOM_submitter_role: session.Session  # noqa NOSONAR
):
    db = dbsession_FOM_submitter_role
    fam_role: model.FamRole = (db.query(model.FamRole).all())[0]

    # add dummy user
    fam_user = model.FamUser(
        **{
            "user_type_code": famConstants.UserType.IDIR,
            "user_name": famConstants.DUMMY_FOREST_CLIENT_NAME,
            "create_user": famConstants.FAM_PROXY_API_USER,
        }
    )
    db.add(fam_user)
    db.flush()

    # add user/role assignment
    user_role_assignment = model.FamUserRoleXref(
        **{
            "user_id": fam_user.user_id,
            "role_id": fam_role.role_id,
            "create_user": famConstants.FAM_PROXY_API_USER,
        }
    )
    db.add(user_role_assignment)
    db.commit()
    yield db

    xref_db_item = (
        db.query(model.FamUserRoleXref)
        .filter(
            model.FamUserRoleXref.user_id == user_role_assignment.user_id,
            model.FamUserRoleXref.role_id == user_role_assignment.role_id,
        )
        .one_or_none()
    )

    if xref_db_item:
        db.delete(xref_db_item)
    db.delete(fam_user)
    db.commit()


@pytest.fixture(scope="function")
def dbsession_fom_dev_application(dbsession_fam_app_environment):
    db = dbsession_fam_app_environment
    fom_dev_application = model.FamApplication(
        **{
            "application_name": "FOM",
            "application_description": "Forest Operations Map",
            "create_user": famConstants.FAM_PROXY_API_USER,
            "app_environment": famConstants.AppEnv.APP_ENV_TYPE_DEV
        }
    )
    db.add(fom_dev_application)
    db.commit()
    yield db

    db.delete(fom_dev_application)
    db.commit()


@pytest.fixture(scope="function")
def dbsession_fom_dev_test_applications(dbsession_fam_app_environment):
    db = dbsession_fam_app_environment
    fom_dev_application = model.FamApplication(
        **{
            "application_name": "fom_dev",
            "application_description": "Forest Operations Map",
            "create_user": famConstants.FAM_PROXY_API_USER,
            "app_environment": famConstants.AppEnv.APP_ENV_TYPE_DEV
        }
    )
    db.add(fom_dev_application)

    fom_test_application = model.FamApplication(
        **{
            "application_name": "fom_test",
            "application_description": "Forest Operations Map",
            "create_user": famConstants.FAM_PROXY_API_USER,
            "app_environment": famConstants.AppEnv.APP_ENV_TYPE_TEST
        }
    )
    db.add(fom_test_application)

    db.commit()
    yield db

    db.delete(fom_test_application)
    db.delete(fom_dev_application)
    db.commit()


@pytest.fixture(scope="function")
def dbsession_FOM_submitter_role(  # noqa NOSONAR
    dbsession_role_types, dbsession_fom_dev_application
):
    db: session.Session = dbsession_fom_dev_application
    fom_dev_application: model.FamApplication = (db.query(model.FamApplication).all())[0]

    # add a role record to db
    fom_submitter_role = model.FamRole(
        **{
            "role_name": FOM_SUBMITTER_ROLE_NAME,
            "role_purpose": "Grant a user access to submit to FOM",
            "create_user": famConstants.FAM_PROXY_API_USER,
            "application_id": fom_dev_application.application_id,
            "role_type_code": famConstants.RoleType.ROLE_TYPE_ABSTRACT,
        }
    )
    db.add(fom_submitter_role)
    db.commit()
    yield db

    role_db_item = (
        db.query(model.FamRole)
        .filter(model.FamRole.role_name == FOM_SUBMITTER_ROLE_NAME)
        .one_or_none()
    )

    if role_db_item:
        db.delete(role_db_item)
        db.commit()


@pytest.fixture(scope="function")
def dbsession_FOM_submitter_role_dev_test(
    dbsession_role_types, dbsession_fom_dev_test_applications
):
    db: session.Session = dbsession_fom_dev_test_applications
    fom_dev_application: model.FamApplication = db.query(model.FamApplication)\
        .filter(model.FamApplication.app_environment == famConstants.AppEnv.APP_ENV_TYPE_DEV).one()
    fom_test_application: model.FamApplication = db.query(model.FamApplication)\
        .filter(model.FamApplication.app_environment == famConstants.AppEnv.APP_ENV_TYPE_TEST).one()

    # add role records to db
    fom_dev_submitter_role = model.FamRole(
        **{
            "role_name": FOM_SUBMITTER_ROLE_NAME,
            "role_purpose": "Grant a user access to submit to FOM",
            "create_user": famConstants.FAM_PROXY_API_USER,
            "application_id": fom_dev_application.application_id,
            "role_type_code": famConstants.RoleType.ROLE_TYPE_ABSTRACT,
        }
    )
    db.add(fom_dev_submitter_role)

    fom_test_submitter_role = model.FamRole(
        **{
            "role_name": FOM_SUBMITTER_ROLE_NAME,
            "role_purpose": "Grant a user access to submit to FOM",
            "create_user": famConstants.FAM_PROXY_API_USER,
            "application_id": fom_test_application.application_id,
            "role_type_code": famConstants.RoleType.ROLE_TYPE_ABSTRACT,
        }
    )
    db.add(fom_test_submitter_role)

    db.commit()
    yield db

    db.query(model.FamRole)\
        .filter(model.FamRole.role_name == FOM_SUBMITTER_ROLE_NAME)\
        .delete()
    db.commit()


@pytest.fixture(scope="function")
def dbsession_concrete_role(dbsession_role_types, dbsession_fom_dev_application):
    db = dbsession_fom_dev_application
    fam_application: model.FamApplication = (db.query(model.FamApplication).all())[0]

    # add a role record to db
    role_name = "Concrete_Test_Role"
    concrete_role = model.FamRole(
        **{
            "role_name": role_name,
            "role_purpose": "Concrete role for application",
            "create_user": famConstants.FAM_PROXY_API_USER,
            "application_id": fam_application.application_id,
            "role_type_code": famConstants.RoleType.ROLE_TYPE_CONCRETE,
        }
    )
    db.add(concrete_role)
    db.commit()
    yield db

    role_db_item = (
        db.query(model.FamRole)
        .filter(model.FamRole.role_name == role_name)
        .one_or_none()
    )

    if role_db_item:
        db.delete(role_db_item)
        db.commit()


@pytest.fixture(scope="function")
def clean_up_all_user_role_assignment(dbsession):
    db = dbsession
    yield db

    # Delete fam_user_role_xref
    stmt = text(
        """
        DELETE FROM fam_user_role_xref
        """
    )
    db.execute(stmt)

    # Then role
    stmt = text(
        """
        DELETE FROM fam_role
        """
    )
    db.execute(stmt)

    # Delete user
    stmt = text(
        """
        DELETE FROM fam_user
        """
    )
    db.execute(stmt)
