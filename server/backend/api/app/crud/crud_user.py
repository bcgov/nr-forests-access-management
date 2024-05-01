import logging

from api.app.models import model as models
from sqlalchemy.orm import Session

from .. import schemas

LOGGER = logging.getLogger(__name__)


def get_users(db: Session):
    """return all the users currently entered into the application

    :param db: _description_
    :type db: Session
    :return: _description_
    :rtype: _type_
    """
    LOGGER.debug(f"db session: {db}")
    fam_users = db.query(models.FamUser).all()
    return fam_users


def get_user(db: Session, user_id: int):
    """gets a specific users record

    :param db: _description_
    :type db: Session
    :param user_id: _description_
    :type user_id: int
    :return: _description_
    :rtype: _type_
    """
    # get a single user based on user_id
    fam_user = (
        db.query(models.FamUser).filter(models.FamUser.user_id == user_id).one_or_none()
    )
    return fam_user


def get_user_by_domain_and_name(
    db: Session, user_type_code: str, user_name: str
) -> models.FamUser:
    # get a single user based on unique combination of user_name and user_type_code.
    fam_user: models.FamUser = (
        db.query(models.FamUser)
        .filter(
            models.FamUser.user_type_code == user_type_code,
            models.FamUser.user_name.ilike(user_name),
        )
        .one_or_none()
    )
    LOGGER.debug(
        f"fam_user {str(fam_user.user_id) + ' found' if fam_user else 'not found'}."
    )
    return fam_user


def create_user(fam_user: schemas.FamUser, db: Session):
    """used to add a new FAM user to the database

    :param fam_user: _description_
    :type fam_user: schemas.FamUser
    :param db: _description_
    :type db: Session
    :return: _description_
    :rtype: _type_
    """
    LOGGER.debug(f"Creating Fam_User: {fam_user}")

    fam_user_dict = fam_user.model_dump()
    db_item = models.FamUser(**fam_user_dict)
    db.add(db_item)
    db.flush()
    return db_item


def find_or_create(
        db: Session,
        user_type_code: str,
        user_name: str,
        requester: str):
    LOGGER.debug(
        f"User - 'find_or_create' with user_type: {user_type_code}, " +
        f"user_name: {user_name}."
    )

    fam_user = get_user_by_domain_and_name(db, user_type_code, user_name)
    if not fam_user:
        request_user = schemas.FamUser(
            **{
                "user_type_code": user_type_code,
                "user_name": user_name,
                "create_user": requester,
            }
        )
        fam_user = create_user(request_user, db)
        LOGGER.debug(f"User created: {fam_user.user_id}.")
        return fam_user

    LOGGER.debug(f"User {fam_user.user_id} found.")
    return fam_user


def get_user_by_cognito_user_id(
    db: Session, cognito_user_id: str
) -> models.FamUser:
    user = (
        db.query(models.FamUser)
        .filter(
            models.FamUser.cognito_user_id == cognito_user_id
        )
        .one_or_none()
    )
    return user


def get_user_by_user_role_xref_id(
    db: Session, user_role_xref_id: int
) -> models.FamUser:
    user = (
        db.query(models.FamUser)
        .join(models.FamUserRoleXref)
        .filter(
            models.FamUserRoleXref.user_role_xref_id == user_role_xref_id,
        )
        .one_or_none()
    )
    return user


def update(
    db: Session, user_id: int, update_values: dict
):
    LOGGER.debug(f"Update on FamUser {user_id} with values: {update_values}")
    update_count = (
        db.query(models.FamUser)
        .filter(models.FamUser.user_id == user_id)
        .update(update_values)
    )
    LOGGER.debug(f"{update_count} row updated.")
    return get_user(db, user_id)
