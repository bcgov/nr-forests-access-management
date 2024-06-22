import logging

from api.app.models import model as models
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

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


def get_user_by_domain_and_guid(
    db: Session, user_type_code: str, user_guid: str
) -> models.FamUser:
    return (
        db.query(models.FamUser)
        .filter(
            models.FamUser.user_type_code == user_type_code,
            models.FamUser.user_guid == user_guid,
        )
        .one_or_none()
    )


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
    db: Session, user_type_code: str, user_name: str, user_guid: str, requester: str
):
    LOGGER.debug(
        f"User - 'find_or_create' with user_type: {user_type_code}, "
        + f"user_name: {user_name}."
    )

    fam_user = get_user_by_domain_and_guid(db, user_type_code, user_guid)
    if not fam_user:
        fam_user_by_domain_and_name = get_user_by_domain_and_name(
            db, user_type_code, user_name
        )
        # if not found user by user_guid, but found user by domain and name
        # in the case of historical FAM user that has no user_guid stored
        # add their user_guid
        if fam_user_by_domain_and_name and not fam_user_by_domain_and_name.user_guid:
            update(
                db,
                fam_user_by_domain_and_name.user_id,
                {models.FamUser.user_guid: user_guid},
                requester,
            )
            LOGGER.debug(
                f"User {fam_user_by_domain_and_name.user_id} found, updated to store their user_guid."
            )
            return fam_user_by_domain_and_name
        # if not found user by user_guid, and not found user by domain and username,
        # or found user by domain and username, but user guid does not match (this is the edge case that could happen when username changed from IDP provider)
        # create a new user
        else:
            request_user = schemas.FamUser(
                **{
                    "user_type_code": user_type_code,
                    "user_name": user_name,
                    "user_guid": user_guid,
                    "create_user": requester,
                }
            )

            fam_user_new = create_user(request_user, db)
            LOGGER.debug(f"User created: {fam_user_new.user_id}.")
            return fam_user_new

    LOGGER.debug(f"User {fam_user.user_id} found.")
    # update user_name if needs
    fam_user = update_user_name(db, fam_user, user_name, requester)
    return fam_user


def get_user_by_cognito_user_id(db: Session, cognito_user_id: str) -> models.FamUser:
    user = (
        db.query(models.FamUser)
        .filter(models.FamUser.cognito_user_id == cognito_user_id)
        .one_or_none()
    )
    return user


def update(
    db: Session, user_id: int, update_values: dict, requester: str  # cognito_user_id
) -> int:
    LOGGER.debug(
        f"Update on FamUser {user_id} with values: {update_values} "
        + f"for requester {requester}"
    )
    update_count = (
        db.query(models.FamUser)
        .filter(models.FamUser.user_id == user_id)
        .update({**update_values, models.FamUser.update_user: requester})
    )
    LOGGER.debug(f"{update_count} row updated.")
    return update_count


def update_user_name(
    db: Session,
    user: models.FamUser,
    user_name_for_update: str,
    requester: str,  # cognito_user_id
):
    if user.user_name.lower() != user_name_for_update.lower():
        update(
            db,
            user.user_id,
            {models.FamUser.user_name: user_name_for_update},
            requester,
        )
        LOGGER.debug(
            f"Updated the username of user {user.user_id} to {user_name_for_update}."
        )
        return get_user(db, user.user_id)
    return user


def update_user_business_guid(
    db: Session, user_id: int, business_guid: str, requester: str  # cognito_user_id
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
        f"update_user_business_guid() with: user_id: {user_id} "
        + f"business_guid: {business_guid} from requester: {requester}"
    )
    if business_guid is not None:
        user = get_user(db, user_id)
        if user.business_guid is None or business_guid != user.business_guid:
            # update user when necessary.
            update(
                db, user_id, {models.FamUser.business_guid: business_guid}, requester
            )
    return get_user(db, user_id)


def fetch_initial_requester_info(
    db: Session,
    cognito_user_id: str
):
    """
    Note!
    The purpose: only to be used to find out initial essential requester information
    for endpoint's checks before endpoint handler being called. Not intended for
    individual crud functions to fetch on this user.

    The quering `user` join other tables for esential information.
    Use orm `joinedload` to join due to the relationship with user is a `lazy`.
    """
    q_stm = (
        select(models.FamUser)
        .options(
            joinedload(models.FamUser.fam_access_control_privileges),
            joinedload(models.FamUser.fam_user_terms_conditions)
        )
        .filter(models.FamUser.cognito_user_id == cognito_user_id)
    )
    user = db.scalars(q_stm).unique().one_or_none()
    return user
