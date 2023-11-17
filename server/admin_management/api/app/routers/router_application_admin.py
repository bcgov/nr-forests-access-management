import logging
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session


from api.app.models import model as models
from api.app.routers.router_guards import get_current_requester, authorize_by_fam_admin, enforce_self_grant_guard
from api.app import database, jwt_validation, schemas
from api.app.schemas import Requester
from api.app.crud import crud_user, curd_application_admin
from api.app.services.application_admin_service import ApplicationAdminService

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.post("",
    response_model=schemas.FamAppAdminGet,
    dependencies=[
        Depends(authorize_by_fam_admin),
        Depends(enforce_self_grant_guard)
    ]
)
def create_application_admin(
    application_admin_request: schemas.FamAppAdminCreate,
    request: Request,
    db: Session = Depends(database.get_db),
    token_claims: dict = Depends(jwt_validation.authorize),
    requester: Requester = Depends(get_current_requester)
):

    LOGGER.debug(
        f"Executing 'create_user_role_assignment' "
        f"with request: {application_admin_request}, requestor: {token_claims}"
    )

    try:
        requesting_user = get_requesting_user(db, requester.cognito_user_id)
        application_admin_service = ApplicationAdminService(db)
        return application_admin_service.create_application_admin(
            application_admin_request, requesting_user.cognito_user_id
        )
        # return curd_application_admin.create_application_admin(
        #     db, application_admin_request, requesting_user.cognito_user_id
        # )

    except Exception as e:
        LOGGER.exception(e)
        raise e


def get_requesting_user(db: Session, cognito_user_id: str) -> models.FamUser:
    requester = crud_user.get_user_by_cognito_user_id(db, cognito_user_id)
    return requester