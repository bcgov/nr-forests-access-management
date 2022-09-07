

import logging

from api.app import constants as famConstants
from api.app.models import model as models
from sqlalchemy.orm import Session

from .. import schemas
from . import crud_role, crud_user

LOGGER = logging.getLogger(__name__)


def createFamUserRoleAssignment(
    request: schemas.FamUserRoleAssignmentCreate,
    db: Session
):
    """
    Create fam_user_role_xref Association

    For initial MVP version:
        FAM api will do a smart insertion to fam_user_role_xref, assume and skip some verification/lookup;
        such as 'forest_client' lookup and 'user' lookup.
    """
    LOGGER.debug(f"Request for user role assignment: {request}")

    famUserRoleXref = models.FamUserRoleXref()
    famUserRoleXref.role_id = request.role_id

    # verify user type in enum (IDIR, BCEID)
    if (request.user_type != famConstants.USER_TYPE['IDIR'] and
       request.user_type != famConstants.USER_TYPE['BCEID']):
        raise Exception(f"Invalid user type: {request.user_type}.")

    # Determine if user already exists or add new user
    famUser = crud_user.getFamUserByDomainAndName(db, request.user_type, request.user_name)
    if not famUser:
        requestUser = schemas.FamUser()
        requestUser.user_type = request.user_type
        requestUser.user_name = request.user_name
        requestUser.create_user = famConstants.FAM_SYSTEM_USER
        famUser = crud_user.createFamUser(requestUser, db)
    LOGGER.debug(f"User for user_role assignment: {famUser}")

    # verifying role exists.
    famRole = crud_role.getFamRole(db, famUserRoleXref.role_id)
    if not famRole:
        raise Exception(f"Role id {famUserRoleXref.role_id} does not exist.")
    LOGGER.debug(f"Role for user_role assignment: {famRole}")

    if request.client_number_id:
        forestClient = (
            db.query(models.FamForestClient)
            .filter(models.FamForestClient.client_number_id == request.client_number_id)
            .one()
        )
        if not forestClient:
            raise Exception(f"Forest Client {request.client_number_id} does not exist.")

    # more TODO...