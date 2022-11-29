import datetime
import logging
from typing import Dict, List, Union

import api.app.models.model as model
import api.app.schemas as schemas
import pytest
import sqlalchemy.exc
from sqlalchemy.orm import session

LOGGER = logging.getLogger(__name__)


@pytest.fixture(scope="function")
def dbSession_famRoles_concrete(dbSession_famRoletype, concreteRoleData_asModel):
    db = dbSession_famRoletype

    # add a record to the database
    db.add(concreteRoleData_asModel)
    # TODO: ideally re-use the db session and remove the commit
    db.commit()
    yield db  # use the session in tests.
    LOGGER.debug(f"newRole: {concreteRoleData_asModel}")
    db.delete(concreteRoleData_asModel)
    db.commit()


@pytest.fixture(scope="function")
def dbSession_famRoletype(
    dbSession: session.Session, abstractRoleTypeRecord, concreteRoleType
):
    db = dbSession
    roleTypeModel_abstract = model.FamRoleType(**abstractRoleTypeRecord)
    db.add(roleTypeModel_abstract)
    roleTypeModel_concrete = model.FamRoleType(**concreteRoleType)
    db.add(roleTypeModel_concrete)

    yield db  # use the session in tests.

    try:
        roleTypeRecord = (
            db.query(model.FamRoleType)
            .filter(
                model.FamRoleType.role_type_code == abstractRoleTypeRecord["role_type_code"] # noqa
            )
            .one()
        )
        db.delete(roleTypeRecord)
        # db.flush()
    except sqlalchemy.exc.InvalidRequestError as e:
        LOGGER.error(f"wasn't committed: {e}")
        db.rollback()

    try:
        roleTypeRecord = (
            db.query(model.FamRoleType)
            .filter(
                model.FamRoleType.role_type_code == concreteRoleType["role_type_code"] # noqa
            )
            .one()
        )
        db.delete(roleTypeRecord)
        # db.flush()
    except sqlalchemy.exc.InvalidRequestError as e:
        LOGGER.debug(f"wasn't committed: {e}")
        db.rollback()


@pytest.fixture(scope="function")
def concreteRoleType() -> Dict[str, Union[str, datetime.datetime]]:
    roleType = {
        "role_type_code": model.FamRoleType.ROLE_TYPE_CONCRETE,
        "description": "describe describe describe",
        "effective_date": datetime.datetime.now(),
    }
    yield roleType

@pytest.fixture(scope="function")
def concreteRoleType_asModel(concreteRoleType) -> model.FamRoleType:
    concreteRoleModel = model.FamRoleType(**concreteRoleType)
    yield concreteRoleModel


# TODO: review duplicate code... remove duplicates with the word 'record' in their names
# TODO: review fixtures that used abstractRoleTypeRecord and then create model to use
#       abstractRoleTypeRecord_asModel, ditto for concrete
@pytest.fixture(scope="function")
def abstractRoleTypeRecord() -> Dict[str, Union[datetime.datetime, str]]:
    roleType = {
        "role_type_code": model.FamRoleType.ROLE_TYPE_ABSTRACT,
        "description": "describe describe describe",
        "effective_date": datetime.datetime.now(),
    }
    yield roleType

@pytest.fixture(scope="function")
def abstractRoleTypeRecord_asModel(abstractRoleTypeRecord) -> model.FamRoleType:
    abstractRoleModel = model.FamRoleType(**abstractRoleTypeRecord)
    yield abstractRoleModel


@pytest.fixture(scope="function")
def concreteRoleData_asPydantic(concreteRoleData) -> schemas.FamRoleCreate:
    famRoleAsPydantic = schemas.FamRoleCreate(**concreteRoleData)
    yield famRoleAsPydantic


@pytest.fixture(scope="function")
def concreteRoleData() -> Dict[str, str]:
    roleData = {
        "role_name": "FAM_ADMIN",
        "role_purpose": "FAM Admin",
        "create_user": "John Doe",
        "role_type_code": model.FamRoleType.ROLE_TYPE_CONCRETE,
    }
    yield roleData


@pytest.fixture(scope="function")
def concreteRoleData_asModel(concreteRoleData) -> Dict[str, str]:
    concreteRole = model.FamRole(**concreteRoleData)
    yield concreteRole


@pytest.fixture(scope="function")
def concreteRoleData2() -> Dict[str, str]:
    roleData = {
        "role_name": "FAM_TEST",
        "role_purpose": "FAM Testing",
        "create_user": "Patrick Roy",
        "role_type_code": model.FamRoleType.ROLE_TYPE_CONCRETE,
    }
    yield roleData


@pytest.fixture(scope="function")
def concreteRoleData2_asModel(concreteRoleData2) -> Dict[str, str]:
    concreteRole = model.FamRole(**concreteRoleData2)
    yield concreteRole


@pytest.fixture(scope="function")
def abstractRoleData() -> Dict[str, str]:
    roleData = {
        "role_name": "FAM_ABS_ROLE",
        "role_purpose": "FAM Testing abstract role",
        "create_user": "PK Subban",
        "role_type_code": model.FamRoleType.ROLE_TYPE_ABSTRACT,
    }
    yield roleData


@pytest.fixture(scope="function")
def abstractRoleData_asModel(abstractRoleData) -> Dict[str, str]:
    abstractRole = model.FamRole(**abstractRoleData)
    yield abstractRole


@pytest.fixture(scope="function")
def deleteAllRoles(dbSession: session.Session) -> None:
    """Cleans up all roles from the database after the test has been run

    :param dbSession: mocked up database session
    :type dbSession: sqlalchemy.orm.session.Session
    """
    yield
    db = dbSession
    famRoles: List[model.FamRole] = db.query(model.FamRole).all()
    for famRole in famRoles:
        db.delete(famRole)
    db.commit()


@pytest.fixture(scope="function")
def deleteAllRoleTypes(dbSession: session.Session) -> None:
    """cleans up all role types from the database"""
    LOGGER.debug(f"dbsession type: {type(dbSession)}")
    yield

    db = dbSession
    famRoles = db.query(model.FamRole).all()
    for famRole in famRoles:
        db.delete(famRole)

    db = dbSession
    famRoleTypes = db.query(model.FamRoleType).all()
    for famRoleType in famRoleTypes:
        db.delete(famRoleType)
    db.commit()
