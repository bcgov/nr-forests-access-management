import logging
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from typing import List


from api.app.models import model as models
from api.app.routers.router_guards import (
    get_current_requester,
    authorize_by_fam_admin,
    enforce_self_grant_guard,
)
from api.app import database, jwt_validation, schemas
from api.app.schemas import Requester
from api.app.services.application_admin_service import ApplicationAdminService
from api.app.services.user_service import UserService

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=schemas.FamAppAdminGet,
    dependencies=[Depends(authorize_by_fam_admin), Depends(enforce_self_grant_guard)],
)
def create_application_admin(
    application_admin_request: schemas.FamAppAdminCreate,
    request: Request,
    db: Session = Depends(database.get_db),
    token_claims: dict = Depends(jwt_validation.authorize),
    requester: Requester = Depends(get_current_requester),
):

    LOGGER.debug(
        f"Executing 'create_user_role_assignment' "
        f"with request: {application_admin_request}, requestor: {token_claims}"
    )

    try:
        application_admin_service = ApplicationAdminService(db)
        requesting_user: models.FamUser = get_requesting_user(
            db, requester.cognito_user_id
        )
        return application_admin_service.create_application_admin(
            application_admin_request, requesting_user.cognito_user_id
        )

    except Exception as e:
        LOGGER.exception(e)
        raise e


@router.delete(
    "/{application_admin_id}",
    response_class=Response,
    dependencies=[Depends(authorize_by_fam_admin), Depends(enforce_self_grant_guard)],
)
def delete_application_admin(
    application_admin_id: int,
    request: Request,
    db: Session = Depends(database.get_db),
    requester: Requester = Depends(get_current_requester),
):
    try:
        application_admin_service = ApplicationAdminService(db)
        return application_admin_service.delete_application_admin(application_admin_id)

    except Exception as e:
        LOGGER.exception(e)
        raise e


@router.get(
    "/{user_id}",
    response_model=List[schemas.FamAppAdminGet],
    status_code=200,
    dependencies=[Depends(authorize_by_fam_admin)],
)
def get_application_admin_by_userid(
    user_id: int,
    db: Session = Depends(database.get_db),
):
    LOGGER.debug(f"Loading application admin access for user_id: {user_id}")
    application_admin_service = ApplicationAdminService(db)
    application_admin_access = (
        application_admin_service.get_application_admin_by_user_id(user_id)
    )
    LOGGER.debug(
        f"Finished loading application admin access - # of results = {len(application_admin_access)}"
    )

    return application_admin_access


def get_requesting_user(db: Session, cognito_user_id: str) -> models.FamUser:
    user_service = UserService(db)
    requester = user_service.get_user_by_cognito_user_id(db, cognito_user_id)
    return requester
