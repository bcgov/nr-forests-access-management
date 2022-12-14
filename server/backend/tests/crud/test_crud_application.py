import datetime
import logging
import os
from typing import Any, Dict, Union

import api.app.schemas as schemas
import sqlalchemy
from api.app.crud import crud_application as crud_application
from api.app.crud import crud_utils
import api.app.constants as constants

LOGGER = logging.getLogger(__name__)


def test_get_applications(
    dbsession_application: sqlalchemy.orm.session.Session,
    application_dict: Dict[str, Union[str, datetime.datetime]],
):
    db = dbsession_application

    LOGGER.debug(f"application_dict: {application_dict}")
    application1 = crud_application.get_application_by_name(
        db=db, application_name=application_dict["application_name"]
    )
    LOGGER.debug(f"application1: {application1}")
    apps = crud_application.get_applications(db=db)

    assert len(apps) == 1
    assert hasattr(apps[0], "application_name")
    assert apps[0].application_name == application_dict["application_name"]


def test_get_application_roles_concrete(
    dbsession_application_concrete_role: sqlalchemy.orm.session.Session,
    application_dict: Dict[str, Union[str, datetime.datetime]],
    application_role_dict: Dict[str, Any],
    concrete_role_dict: Dict[str, Any],
    concrete_role2_dict: Dict[str, Any],
):
    """
    Tests the crud logic that sits behind the get application/roles
    dbSession_famApplication_withRoledata - database session with an test
        application record already loaded to the database, and two roles
    application_dict - A Dictionary describing the application record that is
        to be added to the database
    application_role_dict - A Dictionary that
    """
    # get the application_id from the database for the record that was already
    # added in the fixture dbSession_famApplication_withRoledata, the app id
    # is required to get the roles for that app
    db = dbsession_application_concrete_role
    app = crud_application.get_application_by_name(
        db=db, application_name=application_dict["application_name"]
    )
    LOGGER.debug(f"application_dict: {application_dict}")
    # double check that the app record was populated, and matches with the app
    # record we are expecting
    assert app.application_name == application_dict["application_name"]

    # get the app roles, this is what we want to test.
    app_roles = crud_application.get_application_roles(
        db=db, application_id=app.application_id
    )

    # need to convert this db query to a pydantic to confirm the serialization
    # definitions in schema.py are correct
    role_list = []
    for app_role in app_roles:
        as_schema = schemas.FamApplicationRole.from_orm(app_role)
        role_list.append(as_schema)
        LOGGER.debug(f"app_role: {as_schema.dict()}")
        LOGGER.debug(f"app_role: {as_schema}")

    # assert that the roles we are expecting are present
    assert len(role_list) == 2

    # assert that none of the roles have parents
    for role in role_list:
        assert role.parent_role_id is None

    # get the role names from the returned record
    role_name_list = [role.role_name for role in role_list]
    assert concrete_role_dict["role_name"] in role_name_list
    assert concrete_role2_dict["role_name"] in role_name_list


def test_get_application_roles_abstract(
    dbsession_application_abstract_role: sqlalchemy.orm.session.Session,
    application_dict: Dict[str, Union[str, datetime.datetime]],
    abstract_role_data: Dict[str, str],
    concrete_role_dict: Dict[str, str],
    concrete_role2_dict: Dict[str, str],
):
    """as per:
    https://github.com/bcgov/nr-forests-access-management/issues/126#issuecomment-1325532437
    we do not want the end point to return nested roles atm.  This test
    verifies that this does not happen

    :param dbsession_application_abstract_role: database session with the
        a concrete role (assigned directly to the app), an abstract role, and
        another concrete role that is assigned to the abstract role
    :param application_dict: The data that was used to set up the application
        record that also comes along in the previous fixture.
    """

    db = dbsession_application_abstract_role
    # get the application record so we can retrieve its application-id
    app = crud_application.get_application_by_name(
        db=db, application_name=application_dict["application_name"]
    )
    # using the app-id request the roles associated with it
    app_roles = crud_application.get_application_roles(
        db=db, application_id=app.application_id
    )
    LOGGER.debug(f"app_roles: {app_roles}")
    # should be only two roles returned the abstract one and the concrete one
    app_roles_list = []
    app_role_names = {}
    for app_role in app_roles:
        as_pydantic = schemas.FamApplicationRole.from_orm(app_role)
        app_roles_list.append(as_pydantic)
        app_role_names[as_pydantic.role_name] = as_pydantic
        LOGGER.debug(f"role: {as_pydantic.dict()}")

    LOGGER.debug("appRolesSchema: {appRolesSchemaDict}")
    # expected number of roles returned
    assert len(app_roles_list) == 2
    # assert that the expected abstract role was returned
    assert abstract_role_data["role_name"] in app_role_names
    # assert the purpose / app id / role type code
    LOGGER.debug(f"name: {abstract_role_data['role_name']}")
    LOGGER.debug(f"purpose: {abstract_role_data['role_purpose']}")
    LOGGER.debug(f"app_role_names: {app_role_names[abstract_role_data['role_name']]}")
    assert (
        abstract_role_data["role_purpose"]
        == app_role_names[abstract_role_data["role_name"]].role_purpose
    )
    assert (
        abstract_role_data["role_type_code"]
        == app_role_names[abstract_role_data["role_name"]].role_type_code
    )
    assert (
        app.application_id
        == app_role_names[abstract_role_data["role_name"]].application_id
    )

    # This is a role that was added to the abstract role, so should not show up
    # in the list of roles for the application
    assert concrete_role_dict["role_name"] not in app_role_names

    # checking that the expected concrete role is in the list
    assert concrete_role2_dict["role_name"] in app_role_names
    assert (
        concrete_role2_dict["role_purpose"]
        == app_role_names[concrete_role2_dict["role_name"]].role_purpose
    )
    assert (
        concrete_role2_dict["role_type_code"]
        == app_role_names[concrete_role2_dict["role_name"]].role_type_code
    )
    assert (
        app.application_id
        == app_role_names[concrete_role2_dict["role_name"]].application_id
    )


def test_delete_applications(
    dbsession_application: sqlalchemy.orm.session.Session,
    application_dict: Dict[str, Union[str, datetime.datetime]],
):
    db = dbsession_application
    # get list of applications from the database
    apps = crud_application.get_applications(db=db)
    # iterate over all of them and delete them
    for app in apps:
        crud_application.delete_application(db=db, application_id=app.application_id)

    # finally assert that there are no apps left in the database
    apps_after = crud_application.get_applications(db=db)
    assert len(apps_after) == 0


def test_get_application(
    dbsession_application: sqlalchemy.orm.session.Session,
    application_dict: Dict[str, Union[str, datetime.datetime]],
):
    db = dbsession_application
    apps = crud_application.get_applications(db=db)
    for app in apps:
        app_by_id = crud_application.get_application(
            db=db, application_id=app.application_id
        )
        assert app_by_id.application_id == app.application_id


def test_get_application_by_name(
    dbsession_application: sqlalchemy.orm.session.Session,
    application_dict: Dict[str, Union[str, datetime.datetime]],
):
    db = dbsession_application
    app = crud_application.get_application_by_name(
        db=db, application_name=application_dict["application_name"]
    )
    assert app.application_name == application_dict["application_name"]


# <sqlalchemy.orm.session.Session object at 0x7f9132c507c0>
def test_get_applications_nodata(dbsession: sqlalchemy.orm.session.Session):
    """Was a starting place to figure out crud tests that work with the database
    session, not complete.  Assumes the database starts without any data.

    :param dbsession: sql alchemy database session
    :type dbsession: sqlalchemy.orm.Session
    """
    # TODO: start coding tests for crud.py code.
    files = os.listdir(".")
    LOGGER.debug(f"files: {files}")

    fam_apps = crud_application.get_applications(dbsession)
    assert fam_apps == []
    LOGGER.debug(f"fam_apps: {fam_apps}")


def test_create_application(
    dbsession_delete: sqlalchemy.orm.session.Session,
    application_dict: Dict[str, Union[str, datetime.datetime]],
):
    db = dbsession_delete
    # make sure we are starting off with no records
    fam_apps = crud_application.get_applications(db)
    assert fam_apps == []

    # add the data to the database
    app_data_as_pydantic = schemas.FamApplicationCreate(**application_dict)
    app_data = crud_application.create_application(
        fam_application=app_data_as_pydantic, db=db
    )
    # the object returned by create_application should contain the
    # application object that it was passed
    assert app_data.application_name == application_dict["application_name"]
    # LOGGER.debug(f"app_data: {}")

    # verify that the data is in the database
    fam_apps_after = crud_application.get_applications(db)
    exists = False
    for fam_app_after in fam_apps_after:
        if fam_app_after.application_name == application_dict["application_name"]:
            exists = True
            break

    assert exists


def test_get_application_role_assignments(
    dbsession_application_with_role_user_assignment,
    application_dict,
    user_data_model,
    concrete_role_dict,
    concrete_role2_dict,
    abstract_role_data,
):

    db = dbsession_application_with_role_user_assignment
    app_id = crud_utils.get_application_id_from_name(
        db=db, application_name=application_dict["application_name"]
    )
    LOGGER.debug("app_id is: {app_id}")

    role_assignments = crud_application.get_application_role_assignments(
        db=db, application_id=app_id
    )
    LOGGER.debug(f"role_assignment: {role_assignments}")

    pydantic_role_assignments = []
    # test the schema definitions work, will raise error if they do not
    for role_assignment in role_assignments:
        pydantic_role_assignment = schemas.FamApplicationUserRoleAssignmentGet.from_orm(
            role_assignment
        )
        pydantic_role_assignments.append(pydantic_role_assignment)
        LOGGER.debug(f"roleAssignment: {pydantic_role_assignment.dict()}")

    assert len(role_assignments) == 2
    # same user should belong to both role assignments
    user_properties_2_check = ["user_type_code", "cognito_user_id", "user_name"]
    for pyd_role_assign in pydantic_role_assignments:
        for user_prop in user_properties_2_check:

            assert getattr(pyd_role_assign.user, user_prop) == getattr(
                user_data_model, user_prop
            )
            # make sure the user type related data is included in the response
            assert pyd_role_assign.user.user_type_relation
    role_names = []
    for pyd_role_assign in pydantic_role_assignments:
        # make sure all roles are for the requested application
        assert pyd_role_assign.role.application_id == app_id
        # checking that none of the roles are abstract
        role_assignments[1].role.role_type_code
        assert (
            pyd_role_assign.role.role_type_code == constants.RoleType.ROLE_TYPE_CONCRETE
        )
        role_names.append(pyd_role_assign.role.role_name)

    assert concrete_role_dict["role_name"] in role_names
    assert concrete_role2_dict["role_name"] in role_names
    assert abstract_role_data["role_name"] not in role_names


def test_get_application_role_assignments_wrong_application(
    dbsession_application_with_role_user_assignment, application_dict
):
    db = dbsession_application_with_role_user_assignment
    app_id = crud_utils.get_application_id_from_name(
        db=db, application_name=application_dict["application_name"]
    )
    LOGGER.debug(f"app_id is: {app_id}")

    # get data from a non existant app
    role_assignments = crud_application.get_application_role_assignments(
        db=db, application_id=99
    )
    LOGGER.debug(f"role_assignments: {role_assignments}")
    assert not role_assignments
