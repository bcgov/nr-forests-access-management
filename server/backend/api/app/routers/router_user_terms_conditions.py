import logging
from http import HTTPStatus

from api.app import database
from api.app.crud import crud_user_terms_conditions
from api.app.routers.router_guards import (
    external_delegated_admin_only_action,
    get_current_requester,
)
from api.app.schemas import RequesterSchema
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
    requester: RequesterSchema = Depends(get_current_requester),
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
    db: Session = Depends(database.get_db),
    requester: RequesterSchema = Depends(get_current_requester),
):
    """
    Create a record for terms and conditions acceptance. \n
    If no version is provided, we store the 1st version of the terms and conditions.
    """
    LOGGER.debug(
        f"Create terms and conditions acceptance record for user {requester.user_id}"
    )

    crud_user_terms_conditions.create_user_terms_conditions(
        db, requester.user_id, requester.cognito_user_id
    )
