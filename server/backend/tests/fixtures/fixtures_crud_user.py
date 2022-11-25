import datetime
import logging
import uuid
from typing import TypedDict

import api.app.models.model as model
import api.app.schemas as schemas
import api.app.constants as famConstants
import pytest
from api.app.crud import crud_group as crud_group
from sqlalchemy.orm import session

LOGGER = logging.getLogger(__name__)


class FamUserTD(TypedDict):
    # cludge... ideally this type should be derived from the
    # pydantic model schema.FamUser
    user_type_code: famConstants.UserType
    cognito_user_id: str
    user_name: str
    user_guid: str
    create_user: str
    create_date: datetime.datetime
    update_user: str
    update_date: datetime.datetime


@pytest.fixture(scope="function")
def dbSession_famUserTypes(dbSession, idirUserTypeCodeRecord, bceidUserTypeCodeRecord):
    db = dbSession
    idirUserTypeCode = model.FamUserType(**idirUserTypeCodeRecord)
    bceidUserTypeCode = model.FamUserType(**bceidUserTypeCodeRecord)
    db.add(idirUserTypeCode)
    db.add(bceidUserTypeCode)

    db.commit()
    yield db

    db.delete(idirUserTypeCode)
    db.delete(bceidUserTypeCode)
    db.commit()


@pytest.fixture(scope="function")
def dbSession_famUsers_withdata(
    dbSession_famUserTypes, testUserData3, testGroupData, userGroupXrefData
):
    """to add a user need to satisfy the integrity constraints.

    :param dbSession: _description_
    :type dbSession: _type_
    :param testUserData: _description_
    :type testUserData: _type_
    :param add_group: _description_
    :type add_group: _type_
    :yield: _description_
    :rtype: _type_
    """
    # the following link goes over working with related/associated tables
    # https://www.pythoncentral.io/sqlalchemy-association-tables/

    db = dbSession_famUserTypes
    # trying to add to user without violating the integrity constraint
    # group was populated with a record by the add_group fixture.
    newUser = model.FamUser(**testUserData3)
    groupSchema = model.FamGroup(**testGroupData)
    userGroupXrefData["group"] = groupSchema
    userGroupXrefData["user"] = newUser

    xrefTable = model.FamUserGroupXref(**userGroupXrefData)

    db.add(xrefTable)
    db.commit()

    yield db

    db.delete(xrefTable)
    db.delete(groupSchema)
    db.delete(newUser)
    db.commit()


@pytest.fixture(scope="function")
def testUserData3() -> FamUserTD:
    userData = {
        "user_type_code": famConstants.UserType.BCEID,
        "cognito_user_id": "zzff",
        "user_name": "Billy Smith",
        "user_guid": str(uuid.uuid4()),
        "create_user": "Al Arbour",
    }
    yield userData


@pytest.fixture(scope="function")
def testUserData_asPydantic(testUserData) -> schemas.FamUser:
    famUserAsPydantic = schemas.FamUser(**testUserData)
    yield famUserAsPydantic


@pytest.fixture(scope="function")
def testUserData2_asPydantic(testUserData2) -> schemas.FamUser:
    famUserAsPydantic2 = schemas.FamUser(**testUserData2)
    yield famUserAsPydantic2


@pytest.fixture(scope="function")
def deleteAllUsers(dbSession: session.Session) -> None:
    """Cleans up all users from the database after the test has been run

    :param dbSession: mocked up database session
    :type dbSession: sqlalchemy.orm.session.Session
    """
    LOGGER.debug(f"dbsession type: {type(dbSession)}")
    yield
    db = dbSession
    famUsers = db.query(model.FamUser).all()
    for famUser in famUsers:
        db.delete(famUser)
    db.commit()


@pytest.fixture(scope="function")
def idirUserTypeCodeRecord() -> dict:
    userType = {
        "user_type_code": famConstants.UserType.IDIR,
        "description": "User Type for IDIR users",
    }
    yield userType


@pytest.fixture(scope="function")
def bceidUserTypeCodeRecord() -> dict:
    userType = {
        "user_type_code": famConstants.UserType.BCEID,
        "description": "User Type for IDIR users",
    }
    yield userType


@pytest.fixture(scope="function")
def testUserData() -> dict:

    userData = {
        "user_type_code": famConstants.UserType.BCEID,
        "cognito_user_id": "22ftw",
        "user_name": "Mike Bossy",
        "user_guid": str(uuid.uuid4()),
        "create_user": "Al Arbour",
        "create_date": datetime.datetime.now(),
        "update_user": "Al Arbour",
        "update_date": datetime.datetime.now(),
    }
    yield userData


@pytest.fixture(scope="function")
def testUserData2() -> FamUserTD:
    userData = {
        "user_type_code": famConstants.UserType.BCEID,
        "cognito_user_id": "22dfs",
        "user_name": "Dennis Potvin",
        "user_guid": str(uuid.uuid4()),
        "create_user": "Al Arbour",
        "create_date": datetime.datetime.now(),
        "update_user": "Al Arbour",
        "update_date": datetime.datetime.now(),
    }
    yield userData


@pytest.fixture(scope="function")
def userGroupXrefData():
    nowdatetime = datetime.datetime.now()
    xrefData = {
        "create_user": "serg",
        "create_date": nowdatetime,
        "update_user": "ron",
        "update_date": nowdatetime,
    }
    yield xrefData


@pytest.fixture(scope="function")
def add_group(dbSession, testGroupData):
    db = dbSession
    groupSchema = schemas.FamGroupPost(**testGroupData)

    crud_group.createFamGroup(famGroup=groupSchema, db=db)
    yield db

    db.delete(testGroupData)
    db.commit()


@pytest.fixture(scope="function")
def testGroupData():
    testGroupData = {
        "group_name": "test group",
        "purpose": "testing",
        "create_user": "Brian Trotier",
        "create_date": datetime.datetime.now(),
    }
    return testGroupData
