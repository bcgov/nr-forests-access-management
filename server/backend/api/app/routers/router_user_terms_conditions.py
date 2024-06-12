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


@router.post(
    "/user:validate",
    response_model=bool,
    status_code=HTTPStatus.OK,
)
def if_pass_user_terms_and_conditions_check(
    version: str = "1",
    is_external_delegated_admin: bool = Depends(requester_is_external_delegated_admin),
    db: Session = Depends(database.get_db),
    requester: Requester = Depends(get_current_requester),
):
    """
    Check if user pass the terms and conditions check
    Return True (pass) if user is not external delgated admin
    Return False (not pass) if user is external delegated admin and did not accpet the terms and conditions in the past
    If no version id is provided, we check the 1st version of the terms and conditions
    """
    LOGGER.debug(
        f"Check if user {requester.user_id} needs to accept terms and conditions of version {version}"
    )

    if not is_external_delegated_admin:
        return True
    else:
        return not crud_user_terms_conditions.if_needs_accept_terms_and_conditions(
            db, requester.user_id, version
        )


@router.post(
    "",
    response_model=FamUserTermsConditionsGet,
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
    Create a record for terms and conditions acceptance
    If no version id is provided, we store the 1st version of the terms and conditions
    """
    LOGGER.debug(
        f"Create terms and conditions acceptance record for user {requester.user_id} and version {version}"
    )

    return crud_user_terms_conditions.create_user_terms_conditions(
        db, requester.user_id, version, requester.cognito_user_id
    )
