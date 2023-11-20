import logging
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session


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
        user_service = UserService(db)
        application_admin_service = ApplicationAdminService(db)

        requesting_user: models.FamUser = user_service.get_user_by_cognito_user_id(
            requester.cognito_user_id
        )
        return application_admin_service.create_application_admin(
            application_admin_request, requesting_user.cognito_user_id
        )

    except Exception as e:
        LOGGER.exception(e)
        raise e
