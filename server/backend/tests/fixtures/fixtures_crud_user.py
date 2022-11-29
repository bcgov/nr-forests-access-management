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

# TODO: describe return types, and arg types for methods in this module

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
def dbSession_famUserTypes(dbSession, idirUserTypeCode_Dict, bceidUserTypeCode_Dict):
    db = dbSession
    idirUserTypeCode = model.FamUserType(**idirUserTypeCode_Dict)
    bceidUserTypeCode = model.FamUserType(**bceidUserTypeCode_Dict)
    db.add(idirUserTypeCode)
    db.add(bceidUserTypeCode)

    db.commit()
    yield db

    db.delete(idirUserTypeCode)
    db.delete(bceidUserTypeCode)
    db.commit()


@pytest.fixture(scope="function")
def dbSession_famUsers(
    dbSession_famUserTypes, userData3_Dict, groupData_Dict, userGroupXrefData
):
    """to add a user need to satisfy the integrity constraints.

    :param dbSession_famUserTypes: database session with the user type data
        loaded.
    :type dbSession_famUserTypes: sqlalchemy.orm.session.Session
    :param userData3_Dict: Input dictionary describing a user record
    :type userData3_Dict: dict
    :param groupData_Dict: dictionary describing a group record
    :type groupData_Dict: dict
    :yield: Database session with the user record loaded along with group to
        satisfy the database constraint
    """
    # the following link goes over working with related/associated tables
    # https://www.pythoncentral.io/sqlalchemy-association-tables/

    db = dbSession_famUserTypes
    # trying to add to user without violating the integrity constraint
    # group was populated with a record by the add_group fixture.
    newUser = model.FamUser(**userData3_Dict)
    groupSchema = model.FamGroup(**groupData_Dict)
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
def userData3_Dict() -> FamUserTD:
    userData = {
        "user_type_code": famConstants.UserType.BCEID,
        "cognito_user_id": "zzff",
        "user_name": "Billy Smith",
        "user_guid": str(uuid.uuid4()),
        "create_user": "Al Arbour",
    }
    yield userData


@pytest.fixture(scope="function")
def userData_asPydantic(userData_Dict) -> schemas.FamUser:
    famUserAsPydantic = schemas.FamUser(**userData_Dict)
    yield famUserAsPydantic


@pytest.fixture(scope="function")
def userData2_asPydantic(userData2_Dict) -> schemas.FamUser:
    famUserAsPydantic2 = schemas.FamUser(**userData2_Dict)
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
def idirUserTypeCode_Dict() -> dict:
    userType = {
        "user_type_code": famConstants.UserType.IDIR,
        "description": "User Type for IDIR users",
    }
    yield userType

# TODO: define return type
@pytest.fixture(scope="function")
def idirUserTypeCode_asModel(idirUserTypeCode_Dict) -> model.FamUserType:
    idirUserType = model.FamUserType(**idirUserTypeCode_Dict)
    yield idirUserType


@pytest.fixture(scope="function")
def bceidUserTypeCode_Dict() -> dict:
    userType = {
        "user_type_code": famConstants.UserType.BCEID,
        "description": "User Type for IDIR users",
    }
    yield userType

# TODO: run format on this file, fix format / linter conflicts
# TODO: rename idir user type and this user type so doesn't incldue the word 'record'
@pytest.fixture(scope="function")
def bceidUserTypeCode_asModel(bceidUserTypeCode_Dict):
    bceidUserType = model.FamUserType(**bceidUserTypeCode_Dict)
    yield bceidUserType

@pytest.fixture(scope="function")
def userData_Dict() -> dict:

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

# TODO: standardize the fixture names in this module, remove test from UserData
#       references
@pytest.fixture(scope="function")
def userData_asModel(userData_Dict):
    newUser = model.FamUser(**userData_Dict)
    yield newUser


@pytest.fixture(scope="function")
def userData_asPydantic(userData_Dict) -> schemas.FamUser:
    famUserAsPydantic = schemas.FamUser(**userData_Dict)
    yield famUserAsPydantic


@pytest.fixture(scope="function")
def userData2_Dict() -> FamUserTD:
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
def add_group(dbSession, groupData_Dict):
    db = dbSession
    groupSchema = schemas.FamGroupPost(**groupData_Dict)

    crud_group.createFamGroup(famGroup=groupSchema, db=db)
    yield db

    db.delete(groupData_Dict)
    db.commit()


@pytest.fixture(scope="function")
def groupData_Dict():
    groupData_Dict = {
        "group_name": "test group",
        "purpose": "testing",
        "create_user": "Brian Trotier",
        "create_date": datetime.datetime.now(),
    }
    return groupData_Dict
