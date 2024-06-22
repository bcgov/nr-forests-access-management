import logging
from http import HTTPStatus

from api.app import database
from api.app.constants import CURRENT_TERMS_AND_CONDITIONS_VERSION
from api.app.crud import crud_user_terms_conditions
from api.app.routers.router_guards import (
    external_delegated_admin_only_action, get_current_requester)
from api.app.schemas import Requester
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/user:validate",
    response_model=bool,
    status_code=HTTPStatus.OK,
)
def validate_user_requires_accept_terms_and_conditions(
    requester: Requester = Depends(get_current_requester),
):
    return requester.requires_accept_tc


@router.post(
    "",
    status_code=HTTPStatus.OK,
    dependencies=[
        Depends(external_delegated_admin_only_action),
    ],
)
def create_user_terms_and_conditions(
    version: str = CURRENT_TERMS_AND_CONDITIONS_VERSION,
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
