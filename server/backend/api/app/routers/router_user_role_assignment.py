from http import HTTPStatus
import logging

from api.app.crud import crud_user_role, crud_application
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from .. import database, schemas, jwt_validation

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=schemas.FamUserRoleAssignmentGet)
def create_user_role_assignment(
    role_assignment_request: schemas.FamUserRoleAssignmentCreate,
    db: Session = Depends(database.get_db),
    token_claims: dict = Depends(jwt_validation.authorize),
    requester: str = Depends(jwt_validation.get_request_username)
):
    """
    Create FAM user_role_xref association.
    """
    LOGGER.debug(f"running router ... {db}")

    # Enforce application-level security
    application_id = crud_application.get_application_id_by_role_id(
        db, role_assignment_request.role_id)
    jwt_validation.authorize_by_app_id(application_id, db, token_claims)

    create_data = crud_user_role.create_user_role(
        db, role_assignment_request, requester
    )
    LOGGER.debug(
        "User/Role assignment executed successfully, "
        f"id: {create_data.user_role_xref_id}"
    )
    return create_data


@router.delete(
    "/{user_role_xref_id}",
    status_code=HTTPStatus.NO_CONTENT,
    response_class=Response,
    dependencies=[Depends(jwt_validation.get_request_username)]
)
def delete_user_role_assignment(
    user_role_xref_id: int,
    db: Session = Depends(database.get_db),
    token_claims: dict = Depends(jwt_validation.authorize)
) -> None:
    """
    Delete FAM user_role_xref association.
    """
    """
    Note! There appear to be a bug in FasAPI/Starlette, when http status 204 No-Content is returned (like Delete)
    but, for some reason response still has content and throw error.
    To fix: see this => https://lightrun.com/answers/tiangolo-fastapi-response-content-longer-than-content-length-error-for-delete-and-nocontent
    (response_class=Response) is added to @router.delete with 204 status.
    """

    # Enforce application-level security
    application_id = crud_application.get_application_id_by_user_role_xref_id(
        db, user_role_xref_id)
    jwt_validation.authorize_by_app_id(application_id, db, token_claims)

    crud_user_role.delete_fam_user_role_assignment(db, user_role_xref_id)
    LOGGER.debug(f"User/Role assignment deleted successfully, id: {user_role_xref_id}")
