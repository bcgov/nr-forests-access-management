import operator
from datetime import datetime
from typing import List

from api.app.constants import RoleType, SortOrderEnum
from api.app.models import model as models
from api.app.models.model import FamRole, FamUser, FamUserRoleXref
from sqlalchemy import not_, select
from sqlalchemy.orm import Session
from testspg.constants import TEST_CREATOR


def get_user_role_by_cognito_user_id_and_role_id(
    db: Session, cognito_user_id: str, role_id: int
) -> models.FamUserRoleXref:
    user_role = (
        db.query(models.FamUserRoleXref)
        .join(models.FamUser)
        .filter(
            models.FamUser.cognito_user_id == cognito_user_id,
            models.FamUserRoleXref.role_id == role_id,
        )
        .one_or_none()
    )
    return user_role


def get_existing_testdb_seeded_users(db_pg_session: Session, excluded_user_name_prefix):
    """
    Testcontainer db is up with some existing users (from flyway). If the tests loaded with
    some large amount of test users in db session with name prefixed, this helps to find
    test users exclude pre-existing ones.
    """
    return db_pg_session.scalars(
        select(models.FamUser).filter(not_(models.FamUser.user_name.ilike(f"%{excluded_user_name_prefix}%")))
    ).all()


def get_existing_testdb_seeded_user_roles_assignment(db_pg_session: Session, excluded_user_name_prefix):
    return db_pg_session.scalars(
        select(models.FamUserRoleXref).join(models.FamUser)
        .filter(not_(models.FamUser.user_name.ilike(f"%{excluded_user_name_prefix}%")))
    ).all()


def is_sorted_with(o1, o2, attribute: str, order: SortOrderEnum) -> bool:
    # helper function to compare o1, o2 according to the sorting 'order' on attribute.

    a1 = operator.attrgetter(attribute)(o1)
    a2 = operator.attrgetter(attribute)(o2)
    if a1 is None and a2 is None:
        return True
    if a1 is None:
        return order == SortOrderEnum.DESC
    elif a2 is None:
        return order == SortOrderEnum.ASC
    else:
        return (a1 <= a2 if order == SortOrderEnum.ASC else a1 >= a2)


def contains_any_insensitive(obj, search_attributes: List[str], keyword: str) -> bool:
    # helper function to check if 'keyword' is substring of 'attribute' value, case insensitive.

    def contains_keyword_insensitive(attr: str, keyword: str):
        if attr is None:
            return False
        elif isinstance(attr, str):
            return keyword.lower() in attr.lower()
        elif isinstance(attr, datetime):
            format_string = '%Y-%m-%d %H:%M:%S'
            return keyword.lower() in attr.strftime(format_string)
        else:
            return False

    # return True as long as there is one attribute in the instance containing keyword value
    is_any = any(
        contains_keyword_insensitive(operator.attrgetter(attr_name)(obj), keyword)
        for attr_name in search_attributes)
    return is_any

def create_user(db, user_name, first_name, last_name, user_type_code, user_guid, roles):
    user = FamUser(
        user_name=user_name,
        first_name=first_name,
        last_name=last_name,
        user_type_code=user_type_code,
        user_guid=user_guid,
        create_user=TEST_CREATOR
    )
    db.add(user)
    db.flush()
    for role in roles:
        xref = FamUserRoleXref(user_id=user.user_id, role_id=role.role_id, create_user=TEST_CREATOR)
        db.add(xref)
    db.flush()
    user.fam_user_role_xref = db.query(FamUserRoleXref).filter_by(user_id=user.user_id).all()
    return user

def create_role(db, application_id, role_name, display_name, parent_role=None, forest_client_number=None):
    role = FamRole(
        application_id=application_id,
        role_name=role_name,
        display_name=display_name,
        parent_role=parent_role,
        forest_client_relation=None,
        create_user=TEST_CREATOR,
        role_type_code=RoleType.ROLE_TYPE_CONCRETE
    )
    db.add(role)
    db.flush()
    if forest_client_number:
        from unittest.mock import MagicMock
        role.forest_client_relation = MagicMock()
        role.forest_client_relation.forest_client_number = forest_client_number
    return role