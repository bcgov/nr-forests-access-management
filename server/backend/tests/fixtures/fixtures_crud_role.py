import datetime
import logging
from typing import Dict, Iterator, List, Union

import pytest
import sqlalchemy.exc
from sqlalchemy.orm import session

import api.app.constants as constants
import api.app.models.model as model
import api.app.schemas as schemas

LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def dbsession_fam_roles_concrete(
    dbsession_role_types,
    dbsession_application: session.Session,
    concrete_role_model: model.FamRole
):
    db = dbsession_application
    application: model.FamApplication = db.query(model.FamApplication).one()
    concrete_role_model.application_id = application.application_id

    # add a record to the database
    db.add(concrete_role_model)
    # TODO: ideally re-use the db session and remove the commit
    db.commit()
    yield db  # use the session in tests.
    LOGGER.debug(f"newRole: {concrete_role_model}")
    db.delete(concrete_role_model)
    db.commit()


@pytest.fixture(scope="function")
def dbsession_role_types(
    dbsession: session.Session, abstract_role_type_dict, concrete_role_type_dict
):
    db = dbsession
    role_type_model_abstract = model.FamRoleType(**abstract_role_type_dict)
    db.add(role_type_model_abstract)
    role_type_model_concrete = model.FamRoleType(**concrete_role_type_dict)
    db.add(role_type_model_concrete)

    yield db  # use the session in tests.

    try:
        role_type_record = (
            db.query(model.FamRoleType)
            .filter(
                model.FamRoleType.role_type_code
                == abstract_role_type_dict["role_type_code"]  # noqa
            )
            .one()
        )
        db.delete(role_type_record)
        # db.flush()
    except sqlalchemy.exc.InvalidRequestError as e:
        LOGGER.error(f"wasn't committed: {e}")
        db.rollback()

    try:
        role_type_record = (
            db.query(model.FamRoleType)
            .filter(
                model.FamRoleType.role_type_code
                == concrete_role_type_dict["role_type_code"]  # noqa
            )
            .one()
        )
        db.delete(role_type_record)
        # db.flush()
    except sqlalchemy.exc.InvalidRequestError as e:
        LOGGER.debug(f"wasn't committed: {e}")
        db.rollback()


@pytest.fixture(scope="function")
def concrete_role_type_dict() -> Iterator[Dict[str, Union[str, datetime.datetime]]]:
    role_type = {
        "role_type_code": constants.RoleType.ROLE_TYPE_CONCRETE,
        "description": "describe describe describe",
        "effective_date": datetime.datetime.now(),
    }
    yield role_type


@pytest.fixture(scope="function")
def concrete_role_type_model(concrete_role_type_dict) -> model.FamRoleType:
    concrete_role_model = model.FamRoleType(**concrete_role_type_dict)
    yield concrete_role_model


# TODO: review fixtures that used abstract_role_type_dict and then create model to use
#       abstract_role_type_model, ditto for concrete
@pytest.fixture(scope="function")
def abstract_role_type_dict() -> Iterator[Dict[str, Union[datetime.datetime, str]]]:
    role_type = {
        "role_type_code": constants.RoleType.ROLE_TYPE_ABSTRACT,
        "description": "describe describe describe",
        "effective_date": datetime.datetime.now(),
    }
    yield role_type


@pytest.fixture(scope="function")
def abstract_role_type_model(abstract_role_type_dict) -> model.FamRoleType:
    abstract_role_model = model.FamRoleType(**abstract_role_type_dict)
    yield abstract_role_model


@pytest.fixture(scope="function")
def concrete_role_pydantic(concrete_role_dict) -> schemas.FamRoleCreate:
    fam_role_as_pydantic = schemas.FamRoleCreate(**concrete_role_dict)
    yield fam_role_as_pydantic


@pytest.fixture(scope="function")
def concrete_role_dict() -> Iterator[Dict[str, str]]:
    role_data = {
        "role_name": "FAM_ADMIN",
        "role_purpose": "FAM Admin",
        "application_id": 99999,  # fake id, set it to test id in real testing code.
        "create_user": constants.FAM_PROXY_API_USER,
        "role_type_code": constants.RoleType.ROLE_TYPE_CONCRETE,
    }
    yield role_data


@pytest.fixture(scope="function")
def concrete_role_model(concrete_role_dict) -> model.FamRole:
    concrete_role = model.FamRole(**concrete_role_dict)
    yield concrete_role


@pytest.fixture(scope="function")
def concrete_role2_dict() -> Iterator[Dict[str, str]]:
    role_data = {
        "role_name": "FAM_TEST",
        "role_purpose": "FAM Testing",
        "create_user": constants.FAM_PROXY_API_USER,
        "role_type_code": constants.RoleType.ROLE_TYPE_CONCRETE,
    }
    yield role_data


@pytest.fixture(scope="function")
def concrete_role_with_forest_client() -> Iterator[Dict[str, str]]:
    # "client_number": {
    #     "forest_client_number": '00014903',
    #     "client_name": 'dummy client',
    #     "create_user": 'test_user'
    # }

    role_data = {
        "role_name": "FAM_TEST_FC",
        "role_purpose": "FAM Testing role with forest client",
        "create_user": constants.FAM_PROXY_API_USER,
        "role_type_code": constants.RoleType.ROLE_TYPE_CONCRETE,
        "forest_client_number": '00014903'
    }
    yield role_data


@pytest.fixture(scope="function")
def concrete_role2_model(
    concrete_role2_dict: Iterator[Dict[str, str]]
) -> Iterator[Dict[str, str]]:
    concrete_role = model.FamRole(**concrete_role2_dict)
    yield concrete_role


@pytest.fixture(scope="function")
def abstract_role_data() -> Iterator[Dict[str, str]]:
    role_data = {
        "role_name": "FAM_ABS_ROLE",
        "role_purpose": "FAM Testing abstract role",
        "create_user": constants.FAM_PROXY_API_USER,
        "role_type_code": constants.RoleType.ROLE_TYPE_ABSTRACT,
    }
    yield role_data


@pytest.fixture(scope="function")
def abstract_role_model(abstract_role_data) -> Iterator[Dict[str, str]]:
    abstract_role = model.FamRole(**abstract_role_data)
    yield abstract_role


@pytest.fixture(scope="function")
def delete_all_roles(dbsession: session.Session) -> Iterator[None]:
    """Cleans up all roles from the database after the test has been run

    :param dbsession: mocked up database session
    :type dbsession: sqlalchemy.orm.session.Session
    """
    yield None
    db = dbsession
    fam_roles: List[model.FamRole] = db.query(model.FamRole).all()
    for fam_role in fam_roles:
        db.delete(fam_role)
    db.commit()


@pytest.fixture(scope="function")
def delete_all_role_types(dbsession: session.Session) -> Iterator[None]:
    """cleans up all role types from the database"""
    LOGGER.debug(f"dbsession type: {type(dbsession)}")
    yield None

    db = dbsession
    fam_roles = db.query(model.FamRole).all()
    for fam_role in fam_roles:
        db.delete(fam_role)

    db = dbsession
    fam_role_types = db.query(model.FamRoleType).all()
    for fam_role_type in fam_role_types:
        db.delete(fam_role_type)
    db.commit()
