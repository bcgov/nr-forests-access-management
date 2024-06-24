import logging
from http import HTTPStatus
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.app import database
from api.app.schemas import Requester
from api.app.crud import crud_user_terms_conditions
from api.app.routers.router_guards import (
    get_current_requester,
    external_delegated_admin_only_action,
)


LOGGER = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/user:validate",
    response_model=bool,
    status_code=HTTPStatus.OK,
)
def validate_user_requires_accept_terms_and_conditions(
    version: str = "1",
    db: Session = Depends(database.get_db),
    requester: Requester = Depends(get_current_requester),
):
    """
    Check if user pass the terms and conditions check. \n
    Return False if user is not external delgated admin or already accepted terms and conditions. \n
    Return True if user is external delegated admin and did not accpet the terms and conditions. \n
    If no version is provided, we check the 1st version of the terms and conditions.
    """
    LOGGER.debug(
        f"Check if user {requester} needs to accept terms and conditions of version {version}"
    )

    return crud_user_terms_conditions.require_accept_terms_and_conditions(
        db, requester, version
    )


@router.post(
    "",
    status_code=HTTPStatus.OK,
    dependencies=[
        Depends(external_delegated_admin_only_action),
    ],
)
def create_user_terms_and_conditions(
    version: str = "1",
    db: Session = Depends(database.get_db),
    requester: Requester = Depends(get_current_requester),
):
    """
    Create a record for terms and conditions acceptance. \n
    If no version is provided, we store the 1st version of the terms and conditions.
    """
    LOGGER.debug(
        f"Create terms and conditions acceptance record for user {requester.user_id} and version {version}"
    )

    crud_user_terms_conditions.create_user_terms_conditions(
        db, requester.user_id, version, requester.cognito_user_id
    )
