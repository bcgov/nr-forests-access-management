
import operator

from api.app.constants import SortOrderEnum
from api.app.models import model as models
from sqlalchemy import not_, select
from sqlalchemy.orm import Session


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