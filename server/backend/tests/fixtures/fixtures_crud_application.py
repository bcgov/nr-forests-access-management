import datetime
import logging
import pytest
import sqlalchemy
from typing import Any, Dict, Union, Iterator

import api.app.schemas as schemas
from api.app.crud import crud_application as crud_application
from api.app.crud import crud_role as crud_role
from api.app.models import model as models
import api.app.constants as constants
from api.app.crud import crud_utils

LOGGER = logging.getLogger(__name__)
# TODO: look for application queries that retrieve the app_id and use the
#       crudUtils.get_application_id_from_name method for that


@pytest.fixture(scope="function")
def dbsession_application(
    dbsession_role_types,
    dbsession_fam_app_environment,
    application_dict
) -> sqlalchemy.orm.session.Session:
    db = dbsession_role_types
    application_data1_as_pydantic = schemas.FamApplicationCreate(**application_dict)
    app_data = crud_application.create_application(
        fam_application=application_data1_as_pydantic, db=db
    )
    yield db
    try:
        db.delete(app_data)
        db.commit()
    except sqlalchemy.orm.exc.ObjectDeletedError as e:
        LOGGER.debug("app object was already deleted")
        LOGGER.debug(f"{type(e).__name__}")
        db.rollback()
    except Exception as e:
        LOGGER.debug(f"exception: {e}")
        LOGGER.debug(f"{type(e).__name__}")
        raise


@pytest.fixture(scope="function")
def dbsession_delete(dbsession, application_dict):
    db = dbsession
    yield db

    application_record = (
        db.query(models.FamApplication)
        .filter(
            models.FamApplication.application_name
            == application_dict["application_name"]  # noqa
        )
        .one()
    )
    db.delete(application_record)
    db.flush()


@pytest.fixture(scope="function")
def application_dict() -> Iterator[Dict[str, Union[str, datetime.datetime]]]:
    fam_app_data = {
        "application_name": "FAM",
        "application_description": "a really good app",
        "app_environment": constants.AppEnv.APP_ENV_TYPE_DEV,
        "create_user": constants.FAM_PROXY_API_USER,
        "create_date": datetime.datetime.now(),
        "update_user": "Ron Duguey",
        "update_date": datetime.datetime.now(),
    }
    yield fam_app_data


@pytest.fixture(scope="function")
def dbsession_application_concrete_role(
    dbsession_application: sqlalchemy.orm.session.Session,
    application_dict: Iterator[Dict[str, Union[str, datetime.datetime]]],
    concrete_role_model: models.FamRole,
    concrete_role2_model: models.FamRole,
):
    db = dbsession_application
    db.flush()
    # get the application id
    app_id = crud_utils.get_application_id_from_name(
        db=db, application_name=application_dict["application_name"]  # NOSONAR
    )
    LOGGER.debug(f"app_id is: {app_id}")

    # create a couple of roles for the application
    concrete_role_model.application_id = app_id
    concrete_role2_model.application_id = app_id

    # add the roles to the database
    LOGGER.debug(f"concrete role model: {concrete_role_model}")
    role_data_pydantic = schemas.FamRoleCreate(**concrete_role_model.__dict__)
    rl1 = crud_role.create_role(role=role_data_pydantic, db=db)
    LOGGER.debug(f"rl1: {rl1}")

    role_data_pydantic2 = schemas.FamRoleCreate(**concrete_role2_model.__dict__)
    rl2 = crud_role.create_role(role=role_data_pydantic2, db=db)

    yield db

    db.delete(rl1)
    db.delete(rl2)
    db.commit()


@pytest.fixture(scope="function")
def dbsession_application_abstract_role(
    dbsession_application,
    application_dict,
    abstract_role_model,
    concrete_role_model,
    concrete_role2_model,
) -> sqlalchemy.orm.session.Session:
    """sets up a database session with some nested roles, where the application
    has:
      * 1 concrete roll that is assigned directly to the application
      * 1 abstract role assigned to the application
      * 1 concrete roll that is assigned to the abstract role

    :param dbsession_application: database session with application data
    :param application_dict: the application data that was added to the database
    :param abstract_role_model: orm model object with the abstract role
        that will get added to the database
    :param concrete_role_model: The orm model for the concrete role that
        will get added to the database
    :yield:
    """
    # need to flush so that the app_id pk gets populated
    db = dbsession_application
    db.flush()

    # retrieve the application id, as the roles need to be tied to this app
    app = crud_application.get_application_by_name(
        db=db, application_name=application_dict["application_name"]
    )
    app_id = app.application_id
    LOGGER.debug(f"app_id is: {app_id}")
    # set the app id for the abstract and concrete roles
    abstract_role_model.application_id = app_id
    concrete_role_model.application_id = app_id
    # add the abstract role to the db
    db.add(abstract_role_model)
    db.flush()

    # get the role-id for the abstract role so we can populate the concrete
    # record, ie identify its parent
    abstract_role_record = (
        db.query(models.FamRole)
        .filter(models.FamRole.role_name == abstract_role_model.role_name)
        .one()
    )
    concrete_role_model.parent_role_id = abstract_role_record.role_id
    db.add(concrete_role_model)
    db.flush()

    # get another concrete record, change some of its values and assign it
    # directly to the app
    concrete_role2_model.application_id = app_id
    db.add(concrete_role2_model)
    db.flush()

    yield db

    db.delete(concrete_role_model)
    db.delete(abstract_role_model)
    db.delete(concrete_role2_model)

    db.flush()


@pytest.fixture(scope="function")
def application_role_dict(
        application_dict, concrete_role_type_dict) -> Iterator[Dict[str, Any]]:
    LOGGER.debug(f"concrete_role_type_dict: {concrete_role_type_dict}")
    application_dict["role"] = [concrete_role_type_dict]
    yield application_dict


@pytest.fixture(scope="function")
def dbsession_application_with_role_user_assignment(
    application_dict,
    dbsession_application,
    idir_user_type_code_model,
    bceid_user_type_code_model,
    abstract_role_model,
    concrete_role_model,
    user_data_model,
    forest_client_model,
    concrete_role2_model,
):
    # TODO: add method pydoc
    # TODO: go back to user model and refactor to match other fixtures for naming
    #        ie: userData, userData2, user_data_model, etc...
    #

    # need:
    #   fam_user as a model: user_data_model
    #   fam application: in session
    #   fam_role types: abstract_role_type_model / concrete_role_type_model
    #   fam role as model:
    #   fam user / role x ref as model
    # then merge the models into the app session

    # db session with the application data loaded
    db = dbsession_application
    db.flush()
    # get the application id
    application = (
        db.query(models.FamApplication)
        .filter(
            models.FamApplication.application_name
            == application_dict["application_name"]
        )
        .one()
    )
    application_id = application.application_id
    concrete_role_model.application_id = application_id
    abstract_role_model.application_id = application_id

    db.add(idir_user_type_code_model)
    db.add(bceid_user_type_code_model)
    db.add(user_data_model)
    db.add(concrete_role_model)
    db.add(abstract_role_model)
    db.add(forest_client_model)
    # add forest client record
    db.flush()  # flush required to populate the user_id and role_id pk cols
    # add concrete role under abstract role with the forest client id
    concrete_role2_model.parent_role_id = abstract_role_model.role_id
    concrete_role2_model.client_number_id = forest_client_model.client_number_id
    concrete_role2_model.application_id = application_id
    db.add(concrete_role2_model)
    db.flush()
    user_role_assignment = models.FamUserRoleXref(
        user_id=user_data_model.user_id,
        role_id=concrete_role_model.role_id,
        create_user=constants.FAM_PROXY_API_USER,
    )
    user_role_assignment_nested = models.FamUserRoleXref(
        user_id=user_data_model.user_id,
        role_id=concrete_role2_model.role_id,
        create_user=constants.FAM_PROXY_API_USER,
    )

    db.add(user_role_assignment)
    db.add(user_role_assignment_nested)

    db.flush()

    yield db

    db.delete(user_role_assignment_nested)
    db.delete(user_role_assignment)
    db.delete(concrete_role2_model)
    db.delete(forest_client_model)
    db.delete(abstract_role_model)
    db.delete(concrete_role_model)
    db.delete(user_data_model)
    db.delete(bceid_user_type_code_model)
    db.delete(idir_user_type_code_model)
    db.flush()

@pytest.fixture(scope="function")
def dbsession_fam_app_environment(
    dbsession
):
    db = dbsession

    dev_app_environment = models.FamAppEnvironment(**{
        "app_environment": constants.AppEnv.APP_ENV_TYPE_DEV,
        "description": "DEV",
    })
    test_app_environment = models.FamAppEnvironment(**{
        "app_environment": constants.AppEnv.APP_ENV_TYPE_TEST,
        "description": "TEST",
    })
    prod_app_environment = models.FamAppEnvironment(**{
        "app_environment": constants.AppEnv.APP_ENV_TYPE_PROD,
        "description": "PROD",
    })
    db.add(dev_app_environment)
    db.add(test_app_environment)
    db.add(prod_app_environment)

    db.flush()
    yield db

    db.delete(dev_app_environment)
    db.delete(test_app_environment)
    db.delete(prod_app_environment)
    db.flush()
