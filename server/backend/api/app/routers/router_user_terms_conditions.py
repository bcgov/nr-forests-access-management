import logging
from http import HTTPStatus
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.app import database
from api.app.schemas import Requester, FamUserTermsConditionsGet
from api.app.crud import crud_user_terms_conditions
from api.app.routers.router_guards import (
    get_current_requester,
    external_delegated_admin_only_action,
    requester_is_external_delegated_admin,
)


LOGGER = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/check",
    response_model=bool,
    status_code=HTTPStatus.OK,
)
def if_user_needs_accept_terms_and_conditions(
    version_id: int = 1,
    is_external_delegated_admin: bool = Depends(requester_is_external_delegated_admin),
    db: Session = Depends(database.get_db),
    requester: Requester = Depends(get_current_requester),
):
    """
    Check if user needs to accept the terms and conditions
    If no version id is provided, we check the 1st version of the terms and conditions
    """
    LOGGER.debug(
        f"Check if user {requester.user_id} needs to accept terms and conditions of version {version_id}"
    )

    if is_external_delegated_admin:
        return crud_user_terms_conditions.if_needs_accept_terms_and_conditions(
            db, requester.user_id, version_id
        )
    else:
        return False


@router.post(
    "",
    response_model=FamUserTermsConditionsGet,
    status_code=HTTPStatus.OK,
    dependencies=[
        Depends(external_delegated_admin_only_action),
    ],
)
def create_user_terms_and_conditions(
    version_id: int = 1,
    db: Session = Depends(database.get_db),
    requester: Requester = Depends(get_current_requester),
):
    """
    Create a record for terms and conditions acceptance
    If no version id is provided, we store the 1st version of the terms and conditions
    """
    LOGGER.debug(
        f"Create terms and conditions acceptance record for user {requester.user_id} and version {version_id}"
    )

    return crud_user_terms_conditions.create_user_terms_conditions(
        db, requester.user_id, version_id, requester.cognito_user_id
    )
