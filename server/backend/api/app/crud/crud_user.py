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


def update(
    db: Session, user_id: int, update_values: dict, requester: str  # cognito_user_id
) -> int:
    LOGGER.debug(
        f"Update on FamUser {user_id} with values: {update_values} " +
        f"for requester {requester}"
    )
    update_count = (
        db.query(models.FamUser)
        .filter(models.FamUser.user_id == user_id)
        .update({**update_values, models.FamUser.update_user: requester})
    )
    LOGGER.debug(f"{update_count} row updated.")
    return update_count


def update_user_business_guid(
    db: Session, user_id: int, business_guid: str,
    requester: str  # cognito_user_id
):
    """
    The method only updates business_guid for user if necessary.
    The calling method should make sure "business_guid" is correct for the
    user (e.g.,searched from IDIM). This method does not do BCeID user
    search.
    :param user_id: The user to be updated on.
    :param business_id: The business_guid value to updated for the user.
    :param requester: This is requester's cognito_user_id when updating
        record from the 'update_user'.
    """
    LOGGER.debug(
        f"update_user_business_guid() with: user_id: {user_id} " +
        f"business_guid: {business_guid} from requester: {requester}")
    if business_guid is not None:
        user = get_user(db, user_id)
        if (
            user.business_guid is None
            or business_guid != user.business_guid
        ):
            # update user when necessary.
            update(db, user_id, {
                models.FamUser.business_guid: business_guid
            }, requester)
    return get_user(db, user_id)
