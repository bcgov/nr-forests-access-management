import datetime
import logging
import pytest
import sqlalchemy
from typing import Any, Dict, Generator, Union, Iterator

import api.app.schemas as schemas
from api.app.crud import crud_application as crud_application
from api.app.crud import crud_role as crud_role
from api.app.models import model as models
import api.app.constants as constants
from api.app.crud import crudUtils


LOGGER = logging.getLogger(__name__)
# TODO: look for application queries that retrieve the app_id and use the crudUtils.get_application_id_from_name method for that

@pytest.fixture(scope="function")
def dbSession_famApplication(
    dbSession_famRoletype, applicationData1
) -> sqlalchemy.orm.session.Session:
    db = dbSession_famRoletype
    applicationData1AsPydantic = schemas.FamApplicationCreate(**applicationData1)
    appData = crud_application.createFamApplication(
        famApplication=applicationData1AsPydantic, db=db
    )
    yield db
    try:
        db.delete(appData)
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
def dbsession_delete(dbSession, applicationData1):
    db = dbSession
    yield db

    application_record = (
        db.query(models.FamApplication)
        .filter(
            models.FamApplication.application_name == applicationData1["application_name"] # noqa
        )
        .one()
    )
    db.delete(application_record)


@pytest.fixture(scope="function")
def applicationData1() -> Iterator[
    Dict[str, Union[str, datetime.datetime]]]:
    famAppData = {
        "application_name": "test app",
        "application_description": "a really good app",
        "create_user": constants.FAM_PROXY_API_USER,
        "create_date": datetime.datetime.now(),
        "update_user": "Ron Duguey",
        "update_date": datetime.datetime.now(),
    }
    yield famAppData


@pytest.fixture(scope="function")
def dbSession_famApplication_concreteRoledata(
    dbSession_famApplication,
    applicationData1,
    concreteRoleData_asModel,
    concreteRoleData2_asModel,
):
    db = dbSession_famApplication
    db.flush()
    # get the application id
    app = crud_application.getApplicationByName(
        db=db, application_name=applicationData1["application_name"]
    )
    app_id = app.application_id
    LOGGER.debug(f"app_id is: {app_id}")

    # create a couple of roles for the application
    concreteRoleData_asModel.application_id = app_id
    concreteRoleData2_asModel.application_id = app_id
    # roleData["application_id"] = app_id
    # roleData2["application_id"] = app_id

    # add the roles to the database
    # famRole: schemas.FamRoleCreate, db: Session
    LOGGER.debug(f"simpleRoleData: {concreteRoleData_asModel}")
    # modelDict = dict(concreteRoleData_asModel)
    # LOGGER.debug(f"modelDict: {modelDict}")
    roleDataPydantic = schemas.FamRoleCreate(**concreteRoleData_asModel.__dict__)
    rl1 = crud_role.createFamRole(famRole=roleDataPydantic, db=db)
    LOGGER.debug(f"rl1: {rl1}")

    roleDataPydantic2 = schemas.FamRoleCreate(**concreteRoleData2_asModel.__dict__)
    rl2 = crud_role.createFamRole(famRole=roleDataPydantic2, db=db)
    # LOGGER.debug(f"rl2: {rl2}")

    yield db

    db.delete(rl1)
    db.delete(rl2)
    db.commit()


@pytest.fixture(scope="function")
def dbSession_famApplication_abstractRoledata(
    dbSession_famApplication,
    applicationData1,
    abstractRoleData_asModel,
    concreteRoleData_asModel,
    concreteRoleData2_asModel,
) -> sqlalchemy.orm.session.Session:
    """sets up a database session with some nested roles, where the application
    has:
      * 1 concrete roll that is assigned directly to the application
      * 1 abstract role assigned to the application
      * 1 concrete roll that is assigned to the abstract role

    :param dbSession_famApplication: database session with application data
    :param applicationData1: the application data that was added to the database
    :param abstractRoleData_asModel: orm model object with the abstract role
        that will get added to the database
    :param concreteRoleData_asModel: The orm model for the concrete role that
        will get added to the database
    :yield:
    """
    # need to flush so that the app_id pk gets populated
    db = dbSession_famApplication
    db.flush()

    # retrieve the application id, as the roles need to be tied to this app
    app = crud_application.getApplicationByName(
        db=db, application_name=applicationData1["application_name"]
    )
    app_id = app.application_id
    LOGGER.debug(f"app_id is: {app_id}")
    # set the app id for the abstract and concrete roles
    abstractRoleData_asModel.application_id = app_id
    concreteRoleData_asModel.application_id = app_id
    # add the abstract role to the db
    db.add(abstractRoleData_asModel)
    db.flush()

    # get the role-id for the abstract role so we can populate the concrete
    # record, ie identify its parent
    abstractRoleRecord = (
        db.query(models.FamRole)
        .filter(models.FamRole.role_name == abstractRoleData_asModel.role_name)
        .one()
    )
    concreteRoleData_asModel.parent_role_id = abstractRoleRecord.role_id
    db.add(concreteRoleData_asModel)
    db.flush()

    # get another concrete record, change some of its values and assign it
    # directly to the app
    concreteRoleData2_asModel.application_id = app_id
    db.add(concreteRoleData2_asModel)
    db.flush()

    yield db

    db.delete(concreteRoleData_asModel)
    db.delete(abstractRoleData_asModel)
    db.delete(concreteRoleData2_asModel)

    db.flush()


@pytest.fixture(scope="function")
def applicationRoleData(applicationData1, concreteRoleType) -> Dict[str, Any]:
    LOGGER.debug(f"concreteRoleType: {concreteRoleType}")
    applicationData1["role"] = [concreteRoleType]
    yield applicationData1


@pytest.fixture(scope="function")
def dbSession_famApplication_withRoleUserAssignment(
        applicationData1,
        dbSession_famApplication,
        idirUserTypeCode_asModel,
        bceidUserTypeCode_asModel,
        abstractRoleData_asModel,
        concreteRoleData_asModel,
        concreteRoleType_asModel,
        abstractRoleTypeRecord_asModel,
        userData_asModel,
        forest_client_model,
        concreteRoleData2_asModel):
    # TODO: add method pydoc
    # TODO: go back to user model and refactor to match other fixtures for naming
    #        ie: userData, userData2, userData_asModel, etc...
    #

    # need:
    #   fam_user as a model: userData_asModel
    #   fam application: in session
    #   fam_role types: abstractRoleTypeRecord_asModel / concreteRoleType_asModel
    #   fam role as model:
    #   fam user / role x ref as model
    # then merge the models into the app session

    # db session with the application data loaded
    db = dbSession_famApplication
    db.flush()
    # get the application id
    application = (
        db.query(models.FamApplication)
        .filter(models.FamApplication.application_name ==
                applicationData1['application_name']).one()
    )
    application_id = application.application_id
    concreteRoleData_asModel.application_id = application_id
    abstractRoleData_asModel.application_id = application_id

    db.add(idirUserTypeCode_asModel)
    db.add(bceidUserTypeCode_asModel)
    db.add(userData_asModel)
    #db.add(concreteRoleType_asModel)
    db.add(concreteRoleData_asModel)
    db.add(abstractRoleData_asModel)
    db.add(forest_client_model)
    # add forest client record
    db.flush()  # flush required to populate the user_id and role_id pk cols
    # add concrete role under abstract role with the forest client id
    concreteRoleData2_asModel.parent_role_id = abstractRoleData_asModel.role_id
    concreteRoleData2_asModel.client_number_id = forest_client_model.client_number_id
    concreteRoleData2_asModel.application_id = application_id
    db.add(concreteRoleData2_asModel)
    db.flush()
    user_role_assignment = models.FamUserRoleXref(
        user_id=userData_asModel.user_id,
        role_id=concreteRoleData_asModel.role_id,
        create_user=constants.FAM_PROXY_API_USER
    )
    user_role_assignment_nested = models.FamUserRoleXref(
        user_id=userData_asModel.user_id,
        role_id=concreteRoleData2_asModel.role_id,
        create_user=constants.FAM_PROXY_API_USER
    )

    db.add(user_role_assignment)
    db.add(user_role_assignment_nested)

    db.flush()

    yield db

    db.delete(user_role_assignment_nested)
    db.delete(user_role_assignment)
    db.delete(concreteRoleData2_asModel)
    db.delete(forest_client_model)
    db.delete(abstractRoleData_asModel)
    db.delete(concreteRoleData_asModel)
    db.delete(userData_asModel)
    db.delete(bceidUserTypeCodeRecord_asModel)
    db.delete(idirUserTypeCodeRecord_asModel)
    db.flush()
