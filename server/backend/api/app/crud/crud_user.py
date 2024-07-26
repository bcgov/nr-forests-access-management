import logging
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select

from api.app.constants import UserType, ApiInstanceEnv, IdimSearchUserParamType
from api.app.models import model as models
from api.app.crud import crud_utils
from api.app.integration.idim_proxy import IdimProxyService
from api.config import config

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


def update_user_properties_from_verified_target_user(
    db: Session,
    user_id: int,
    target_user: schemas.TargetUser,
    requester: str,  # cognito_user_id
):
    """
    This is to update fam_user's properties from verified_target_user.
    'verified_target_user' user is searched from IDIM proxy service.
    Currently few properties are updated. 'user_name' is left out for different update.
    :param user_id: The user to be updated on.
    :param target_user: Type of TargetUser.
        Contains the user's latest property values for update.
    :param requester: This is requester's cognito_user_id when updating
        record from the 'update_user'.
    """
    user_type_code = target_user.user_type_code
    # update first_name, last_name, email
    first_name = target_user.first_name
    last_name = target_user.last_name
    email = target_user.email
    LOGGER.debug(
        f"Add first_name: {first_name}, last_name: {last_name}, "
        f"email: {email} for fam_user update."
    )
    properties_to_update = {
        models.FamUser.first_name: first_name,
        models.FamUser.last_name: last_name,
        models.FamUser.email: email,
    }
    # update business_guid when necessary
    business_guid = target_user.business_guid
    if user_type_code == UserType.BCEID and business_guid:
        LOGGER.debug(f"Add business_guid: {business_guid} for fam_user update.")
        # add additional property to 'properties_to_update'
        properties_to_update = {
            **properties_to_update,
            models.FamUser.business_guid: business_guid,
        }

    update(db, user_id, properties_to_update, requester)
    LOGGER.debug(f"fam_user {user_id} properties were updated.")
    return get_user(db, user_id)


def fetch_initial_requester_info(db: Session, cognito_user_id: str):
    """
    Note!
    The purpose: only to be used to find out initial essential requester information
    for endpoint's checks before endpoint handler being called. Not intended for
    individual crud functions to fetch on this user.

    The quering `user` join other tables for essential information.
    Use orm `joinedload` to join due to the relationship with user is a `lazy`.
    """
    q_stm = (
        select(models.FamUser)
        .options(
            joinedload(models.FamUser.fam_access_control_privileges),
            joinedload(models.FamUser.fam_user_terms_conditions),
        )
        .filter(models.FamUser.cognito_user_id == cognito_user_id)
    )
    user = db.scalars(q_stm).unique().one_or_none()
    return user


def update_user_info_from_idim_source(
    db: Session, use_pagination: bool, page: int, per_page: int
) -> schemas.FamUserUpdateResponse:
    """
    Go through each user record in the database,
    update the user information to match the record in IDIM web service,
    only for IDIR and Business BCeID users, ignore bc service card users
    """
    # get a requester from the database
    requester = (
        db.query(models.FamUser)
        .filter(
            models.FamUser.user_name == config.get_requester_name_for_update_user_info()
        )
        .one_or_none()
    )
    # setup IDIM web service
    api_instance_env = (
        ApiInstanceEnv.PROD if crud_utils.is_on_aws_prod() else ApiInstanceEnv.TEST
    )
    idim_proxy_service = IdimProxyService(requester, api_instance_env)

    # grab fam users from user table
    fam_users = get_users(db)
    total_db_users_count = len(fam_users)
    LOGGER.debug(f"Total number of users in database: {total_db_users_count}")

    if use_pagination:
        fam_users = (
            db.query(models.FamUser)
            .order_by(models.FamUser.user_id.asc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        LOGGER.debug(
            f"Updating information for users on page {page}, there are {per_page} users on each page"
        )

    success_user_list = []
    failed_user_list = []
    ignored_user_list = []  # we ignore for bcsc users, cause IDIM does not provide bcsc users information
    mismatch_user_list = []  # for the users whose user_guid record does not match the user_guid from IDIM

    for user in fam_users:
        try:
            LOGGER.debug(
                f"Updating information for user: {user.user_name}, type: {user.user_type_code}, guid: {user.user_guid}"
            )
            search_result = None
            properties_to_update = {}

            if user.user_type_code == UserType.IDIR:
                # IDIM web service doesn't support search IDIR by user_guid, so we search by userID
                search_result = idim_proxy_service.search_idir(
                    schemas.IdimProxySearchParam(**{"userId": user.user_name})
                )

                if not user.user_guid:
                    # if user has no user_guid in our database, add it
                    properties_to_update = {
                        models.FamUser.user_guid: search_result.get("guid"),
                    }

                if search_result and search_result.get("found") and user.user_guid != search_result.get("guid"):
                    # if found user's user_guid does not match our record
                    # which is the edge case that could cause by the username change, ignore this situation
                    # only IDIR user has this edge case, because IDIM does not support search IDIR by user_guid
                    mismatch_user_list.append(user.user_id)
                    LOGGER.debug(
                        f"Updating information for user {user.user_name} is ignored because the user_guid does not match"
                    )
                    continue

            elif user.user_type_code == UserType.BCEID:
                if user.user_guid:
                    # if found business bceid user by user_guid, update username if necessary
                    search_result = idim_proxy_service.search_business_bceid(
                        schemas.IdimProxyBceidSearchParam(
                            **{
                                "searchUserBy": IdimSearchUserParamType.USER_GUID,
                                "searchValue": user.user_guid,
                            }
                        )
                    )
                    properties_to_update = {
                        models.FamUser.user_name: search_result.get("userId"),
                    }

                else:
                    # if user has no user_guid in our database, find by user_name and add user_guid to database
                    search_result = idim_proxy_service.search_business_bceid(
                        schemas.IdimProxyBceidSearchParam(
                            **{
                                "searchUserBy": IdimSearchUserParamType.USER_ID,
                                "searchValue": user.user_name,
                            }
                        )
                    )
                    properties_to_update = {
                        models.FamUser.user_guid: search_result.get("guid"),
                    }
            else:
                # ignore bc service card users
                ignored_user_list.append(user.user_id)
                LOGGER.debug(
                    f"Updating information for user {user.user_name} is ignored because we only focus on IDIR and Business BCeID"
                )
                continue

            # Update various target_user fields from idim search if exists
            if search_result and search_result.get("found"):
                properties_to_update = {
                    **properties_to_update,
                    models.FamUser.first_name: search_result.get("firstName"),
                    models.FamUser.last_name: search_result.get("lastName"),
                    models.FamUser.email: search_result.get("email"),
                    models.FamUser.business_guid: search_result.get("businessGuid"),
                }

                update(
                    db, user.user_id, properties_to_update, requester.cognito_user_id
                )
                LOGGER.debug(f"Updating information for user {user.user_name} is done")
                success_user_list.append(user.user_id)
            else:
                LOGGER.debug(
                    f"Cannot find user {user.user_name} {user.user_guid} with user type {user.user_type_code}"
                )
                failed_user_list.append(user.user_id)

        except Exception as e:
            LOGGER.debug(f"Failed to update user info: {e}")
            failed_user_list.append(user.user_id)

    return schemas.FamUserUpdateResponse(
        **{
            "total_db_users_count": total_db_users_count,
            "current_page": page,
            "users_count_on_page": len(fam_users),
            "success_user_id_list": success_user_list,
            "failed_user_id_list": failed_user_list,
            "ignored_user_id_list": ignored_user_list,
            "mismatch_user_list": mismatch_user_list,
        }
    )
