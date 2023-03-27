import datetime
import logging
import uuid
from typing import Any, Dict, Iterator, TypedDict, Union

import api.app.constants as famConstants
import api.app.models.model as model
import api.app.schemas as schemas
import pytest
import tests.tests.test_constants as testConstants
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
def dbsession_fam_user_types(
    dbsession, idir_user_type_code_dict, bceid_user_type_code_dict
):
    db = dbsession
    idir_user_type_code = model.FamUserType(**idir_user_type_code_dict)
    bceid_user_type_code = model.FamUserType(**bceid_user_type_code_dict)
    db.add(idir_user_type_code)
    db.add(bceid_user_type_code)

    db.commit()
    yield db

    db.delete(idir_user_type_code)
    db.delete(bceid_user_type_code)
    db.commit()


@pytest.fixture(scope="function")
def dbsession_fam_users(
    dbsession_fam_user_types,
    user_data3_dict: Dict[str, Any],
    group_dict,
    user_group_xref_dict,
):
    """to add a user need to satisfy the integrity constraints.

    :param dbsession_fam_user_types: database session with the user type data
        loaded.
    :type dbsession_fam_user_types: sqlalchemy.orm.session.Session
    :param user_data3_dict: Input dictionary describing a user record
    :type user_data3_dict: Dict[str, Any]
    :param group_dict: dictionary describing a group record
    :type group_dict: dict
    :yield: Database session with the user record loaded along with group to
        satisfy the database constraint
    """
    # the following link goes over working with related/associated tables
    # https://www.pythoncentral.io/sqlalchemy-association-tables/

    db = dbsession_fam_user_types
    # trying to add to user without violating the integrity constraint
    # group was populated with a record by the add_group fixture.
    new_user = model.FamUser(**user_data3_dict)
    group_schema = model.FamGroup(**group_dict)
    user_group_xref_dict["group"] = group_schema
    user_group_xref_dict["user"] = new_user

    xref_table = model.FamUserGroupXref(**user_group_xref_dict)

    db.add(xref_table)
    db.commit()

    yield db

    db.delete(xref_table)
    db.delete(group_schema)
    db.delete(new_user)
    db.commit()


@pytest.fixture(scope="function")
def user_data3_dict() -> Iterator[Dict[str, Union[str, famConstants.UserType]]]:
    user_data = {
        "user_type_code": famConstants.UserType.BCEID,
        "cognito_user_id": "zzff",
        "user_name": "BSMITH",
        "user_guid": str(uuid.uuid4()),
        "create_user": testConstants.FAM_PROXY_API_USER,
    }
    # return user_data
    # try return instead? yield user_data
    yield user_data


@pytest.fixture(scope="function")
def userdata_pydantic(user_data_dict) -> schemas.FamUser:
    fam_user_pydantic = schemas.FamUser(**user_data_dict)
    yield fam_user_pydantic


@pytest.fixture(scope="function")
def userdata2_pydantic(user_data2_dict) -> schemas.FamUser:
    fam_user_as_pydantic2 = schemas.FamUser(**user_data2_dict)
    yield fam_user_as_pydantic2


@pytest.fixture(scope="function")
def delete_all_users(dbsession: session.Session) -> Iterator[None]:
    """Cleans up all users from the database after the test has been run

    :param dbsession: mocked up database session
    :type dbsession: sqlalchemy.orm.session.Session
    """
    LOGGER.debug(f"dbsession type: {type(dbsession)}")
    yield None
    db = dbsession
    fam_users = db.query(model.FamUser).all()
    for fam_user in fam_users:
        db.delete(fam_user)
    db.commit()


@pytest.fixture(scope="function")
def idir_user_type_code_dict() -> Iterator[Dict[str, str]]:
    user_type = {
        "user_type_code": famConstants.UserType.IDIR,
        "description": "IDIR",
    }
    yield user_type


# TODO: define return type
@pytest.fixture(scope="function")
def idir_user_type_code_model(idir_user_type_code_dict) -> model.FamUserType:
    idir_user_type = model.FamUserType(**idir_user_type_code_dict)
    yield idir_user_type


@pytest.fixture(scope="function")
def bceid_user_type_code_dict() -> Iterator[Dict[str, str]]:
    user_type = {
        "user_type_code": famConstants.UserType.BCEID,
        "description": "BCeID",
    }
    yield user_type


# TODO: run format on this file, fix format / linter conflicts
# TODO: rename idir user type and this user type so doesn't incldue the word 'record'
@pytest.fixture(scope="function")
def bceid_user_type_code_model(bceid_user_type_code_dict):
    bceid_user_type = model.FamUserType(**bceid_user_type_code_dict)
    yield bceid_user_type


@pytest.fixture(scope="function")
def user_data_dict() -> Iterator[Dict[str, Union[str, datetime.datetime]]]:

    user_data = {
        "user_type_code": famConstants.UserType.BCEID,
        "cognito_user_id": "22ftw",
        "user_name": "MBOSSY",
        "user_guid": str(uuid.uuid4()),
        "create_user": testConstants.FAM_PROXY_API_USER,
        "create_date": datetime.datetime.now(),
        "update_user": testConstants.FAM_PROXY_API_USER,
        "update_date": datetime.datetime.now(),
    }
    yield user_data


# TODO: standardize the fixture names in this module, remove test from UserData
#       references
@pytest.fixture(scope="function")
def user_data_model(user_data_dict):
    new_user = model.FamUser(**user_data_dict)
    yield new_user


@pytest.fixture(scope="function")
def user_data2_dict() -> Iterator[FamUserTD]:
    user_data = {
        "user_type_code": famConstants.UserType.BCEID,
        "cognito_user_id": "22dfs",
        "user_name": "DPOTVIN",
        "user_guid": str(uuid.uuid4()),
        "create_user": testConstants.FAM_PROXY_API_USER,
        "create_date": datetime.datetime.now(),
        "update_user": testConstants.FAM_PROXY_API_USER,
        "update_date": datetime.datetime.now(),
    }
    yield user_data


@pytest.fixture(scope="function")
def user_group_xref_dict() -> Iterator[Dict[str, Union[datetime.datetime, str]]]:
    nowdatetime = datetime.datetime.now()
    x_ref_data = {
        "create_user": testConstants.FAM_PROXY_API_USER,
        "create_date": nowdatetime,
        "update_user": testConstants.FAM_PROXY_API_USER,
        "update_date": nowdatetime,
    }
    yield x_ref_data


@pytest.fixture(scope="function")
def add_group(dbsession, group_dict):
    db = dbsession
    group_schema = schemas.FamGroupPost(**group_dict)

    crud_group.createFamGroup(famGroup=group_schema, db=db)
    yield db

    db.delete(group_dict)
    db.commit()


@pytest.fixture(scope="function")
def group_dict() -> Iterator[Dict[str, Union[str, datetime.datetime]]]:
    group_dict = {
        "group_name": "test group",
        "purpose": "testing",
        "create_user": testConstants.FAM_PROXY_API_USER,
        "create_date": datetime.datetime.now(),
    }
    yield group_dict
