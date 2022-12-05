import datetime
import logging
import os
from typing import Any, Dict, Union

import api.app.schemas as schemas
import sqlalchemy
from api.app.crud import crud_application as crud_application
from api.app.crud import crudUtils

LOGGER = logging.getLogger(__name__)


def test_getFamApplications(
    dbSession_famApplication: sqlalchemy.orm.session.Session,
    applicationData1: Dict[str, Union[str, datetime.datetime]],
):
    db = dbSession_famApplication

    LOGGER.debug(f"applicationData1: {applicationData1}")
    application1 = crud_application.getApplicationByName(
        db=db, application_name=applicationData1["application_name"]
    )
    LOGGER.debug(f"application1: {application1}")
    apps = crud_application.getFamApplications(db=db)

    assert len(apps) == 1
    assert hasattr(apps[0], "application_name")
    assert apps[0].application_name == applicationData1["application_name"]


def test_getFamApplicationRoles_concrete(
    dbSession_famApplication_concreteRoledata: sqlalchemy.orm.session.Session,
    applicationData1: Dict[str, Union[str, datetime.datetime]],
    applicationRoleData: Dict[str, Any],
    concreteRoleData: Dict[str, Any],
    concreteRoleData2: Dict[str, Any],
):
    """
    Tests the crud logic that sits behind the get application/roles
    dbSession_famApplication_withRoledata - database session with an test
        application record already loaded to the database, and two roles
    applicationData1 - A Dictionary describing the application record that is
        to be added to the database
    applicationRoleData - A Dictionary that
    """
    # get the application_id from the database for the record that was already
    # added in the fixture dbSession_famApplication_withRoledata, the app id
    # is required to get the roles for that app
    db = dbSession_famApplication_concreteRoledata
    app = crud_application.getApplicationByName(
        db=db, application_name=applicationData1["application_name"]
    )
    LOGGER.debug(f"applicationData1: {applicationData1}")
    # double check that the app record was populated, and matches with the app
    # record we are expecting
    assert app.application_name == applicationData1["application_name"]

    # get the app roles, this is what we want to test.
    appRoles = crud_application.getFamApplicationRoles(
        db=db, application_id=app.application_id
    )

    # need to convert this db query to a pydantic to confirm the serialization
    # definitions in schema.py are correct
    roleList = []
    for appRole in appRoles:
        asSchema = schemas.FamApplicationRole.from_orm(appRole)
        roleList.append(asSchema)
        LOGGER.debug(f"appRole: {asSchema.dict()}")
        LOGGER.debug(f"appRole: {asSchema}")

    # assert that the roles we are expecting are present
    assert len(roleList) == 2

    # assert that none of the roles have parents
    for role in roleList:
        assert role.parent_role_id is None

    # get the role names from the returned record
    role_name_list = [role.role_name for role in roleList]
    assert concreteRoleData["role_name"] in role_name_list
    assert concreteRoleData2["role_name"] in role_name_list


def test_getFamApplicationRoles_abstract(
    dbSession_famApplication_abstractRoledata: sqlalchemy.orm.session.Session,
    applicationData1: Dict[str, Union[str, datetime.datetime]],
    abstractRoleData: Dict[str, str],
    concreteRoleData: Dict[str, str],
    concreteRoleData2: Dict[str, str],
):
    """as per:
    https://github.com/bcgov/nr-forests-access-management/issues/126#issuecomment-1325532437
    we do not want the end point to return nested roles atm.  This test
    verifies that this does not happen

    :param dbSession_famApplication_abstractRoledata: database session with the
        a concrete role (assigned directly to the app), an abstract role, and
        another concrete role that is assigned to the abstract role
    :param applicationData1: The data that was used to set up the application
        record that also comes along in the previous fixture.
    """

    db = dbSession_famApplication_abstractRoledata
    # get the application record so we can retrieve its application-id
    app = crud_application.getApplicationByName(
        db=db, application_name=applicationData1["application_name"]
    )
    # using the app-id request the roles associated with it
    appRoles = crud_application.getFamApplicationRoles(
        db=db, application_id=app.application_id
    )
    LOGGER.debug(f"appRoles: {appRoles}")
    # should be only two roles returned the abstract one and the concrete one
    appRolesList = []
    appRoleNames = {}
    for appRole in appRoles:
        asPydantic = schemas.FamApplicationRole.from_orm(appRole)
        appRolesList.append(asPydantic)
        appRoleNames[asPydantic.role_name] = asPydantic
        LOGGER.debug(f"role: {asPydantic.dict()}")

    LOGGER.debug("appRolesSchema: {appRolesSchemaDict}")
    # expected number of roles returned
    assert len(appRolesList) == 2
    # assert that the expected abstract role was returned
    assert abstractRoleData["role_name"] in appRoleNames
    # assert the purpose / app id / role type code
    LOGGER.debug(f"name: {abstractRoleData['role_name']}")
    LOGGER.debug(f"purpose: {abstractRoleData['role_purpose']}")
    LOGGER.debug(f"appRoleNames: {appRoleNames[abstractRoleData['role_name']]}")
    assert (
        abstractRoleData["role_purpose"] ==
        appRoleNames[abstractRoleData["role_name"]].role_purpose
    )
    assert (
        abstractRoleData["role_type_code"] ==
        appRoleNames[abstractRoleData["role_name"]].role_type_code
    )
    assert (
        app.application_id == appRoleNames[abstractRoleData["role_name"]].application_id
    )

    # This is a role that was added to the abstract role, so should not show up
    # in the list of roles for the application
    assert concreteRoleData["role_name"] not in appRoleNames

    # checking that the expected concrete role is in the list
    assert concreteRoleData2["role_name"] in appRoleNames
    assert (
        concreteRoleData2["role_purpose"] ==
        appRoleNames[concreteRoleData2["role_name"]].role_purpose
    )
    assert (
        concreteRoleData2["role_type_code"] ==
        appRoleNames[concreteRoleData2["role_name"]].role_type_code
    )
    assert (
        app.application_id ==
        appRoleNames[concreteRoleData2["role_name"]].application_id
    )


def test_deleteFamApplications(
    dbSession_famApplication: sqlalchemy.orm.session.Session,
    applicationData1: Dict[str, Union[str, datetime.datetime]],
):
    db = dbSession_famApplication
    # get list of applications from the database
    apps = crud_application.getFamApplications(db=db)
    # iterate over all of them and delete them
    for app in apps:
        crud_application.deleteFamApplication(db=db, application_id=app.application_id)

    # finally assert that there are no apps left in the database
    appsAfter = crud_application.getFamApplications(db=db)
    assert len(appsAfter) == 0


def test_getFamApplication(
    dbSession_famApplication: sqlalchemy.orm.session.Session,
    applicationData1: Dict[str, Union[str, datetime.datetime]],
):
    db = dbSession_famApplication
    apps = crud_application.getFamApplications(db=db)
    for app in apps:
        appById = crud_application.getFamApplication(
            db=db, application_id=app.application_id
        )
        assert appById.application_id == app.application_id


def test_getFamApplicationByName(
    dbSession_famApplication: sqlalchemy.orm.session.Session,
    applicationData1: Dict[str, Union[str, datetime.datetime]],
):
    db = dbSession_famApplication
    app = crud_application.getApplicationByName(
        db=db, application_name=applicationData1["application_name"]
    )
    assert app.application_name == applicationData1["application_name"]


# <sqlalchemy.orm.session.Session object at 0x7f9132c507c0>
def test_getFamApplications_nodata(dbSession: sqlalchemy.orm.session.Session):
    """Was a starting place to figure out crud tests that work with the database
    session, not complete.  Assumes the database starts without any data.

    :param dbSession: sql alchemy database session
    :type dbSession: sqlalchemy.orm.Session
    """
    # TODO: start coding tests for crud.py code.
    files = os.listdir(".")
    LOGGER.debug(f"files: {files}")

    famApps = crud_application.getFamApplications(dbSession)
    assert famApps == []
    LOGGER.debug(f"famApps: {famApps}")


def test_createFamApplication(
    dbsession_delete: sqlalchemy.orm.session.Session,
    applicationData1: Dict[str, Union[str, datetime.datetime]],
):
    db = dbsession_delete
    # make sure we are starting off with no records
    famApps = crud_application.getFamApplications(db)
    assert famApps == []

    # add the data to the database
    appDataAsPydantic = schemas.FamApplicationCreate(**applicationData1)
    appData = crud_application.createFamApplication(
        famApplication=appDataAsPydantic, db=db
    )
    # the object returned by createFamApplication should contain the
    # application object that it was passed
    assert appData.application_name == applicationData1["application_name"]
    # LOGGER.debug(f"appData: {}")

    # verify that the data is in the database
    famAppsAfter = crud_application.getFamApplications(db)
    exists = False
    for famAppAfter in famAppsAfter:
        if famAppAfter.application_name == applicationData1["application_name"]:
            exists = True
            break

    assert exists


def test_get_fam_application_role_assignments(
        dbSession_famApplication_withRoleUserAssignment,
        applicationData1
        ):
    # TODO: come back and complete this test, grab code from router test for this end point
    db = dbSession_famApplication_withRoleUserAssignment
    app_id = crudUtils.get_application_id_from_name(db=db, application_name=applicationData1['application_name'])
    LOGGER.debug("app_id is: {app_id}")


    role_assignments = crud_application.getFamApplicationRoleAssignments(
        db=db,
        application_id=app_id)
    LOGGER.debug(f"role_assignment: {role_assignments}")

    # test the schema
    for role_assignment in role_assignments:
        roleAssignment = schemas.FamApplicationUserRoleAssignmentGet.from_orm(role_assignment)
        LOGGER.debug(f"roleAssignment: {roleAssignment.dict()}")

    # TODO: add a bunch of assertions
    pass
    # TODO: add a test that creates a role for a different application and
    # make sure it is not returned