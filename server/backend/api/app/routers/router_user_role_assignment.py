from http import HTTPStatus
import logging

from api.app.crud import crud_user_role
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from .. import dependencies, schemas

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.post("", response_model=schemas.FamUserRoleAssignmentGet)
def create_user_role_assignment(
    userRoleAssignmentRequset: schemas.FamUserRoleAssignmentCreate,
    db: Session = Depends(dependencies.get_db),
):
    """
    Create FAM user_role_xref association.
    """
    LOGGER.debug(f"running router ... {db}")
    createData = crud_user_role.createFamUserRoleAssignment(
        db, userRoleAssignmentRequset
    )
    LOGGER.debug(
        "User/Role assignment executed successfully, "
        f"id: {createData.user_role_xref_id}"
    )
    return createData


@router.delete(
    "/{user_role_xref_id}",
    status_code=HTTPStatus.NO_CONTENT,
    response_class=Response
)
def delete_user_role_assignment(
    user_role_xref_id: int, db: Session = Depends(dependencies.get_db)
) -> None:
    """
    Delete FAM user_role_xref association.
    """
    """
    Note! Ther appear to be a bug in FasAPI/Starlette, when there is 204 No-Content code (like Delete)
    but for some reason response still has content and throw error. 
    To fix: see this => https://lightrun.com/answers/tiangolo-fastapi-response-content-longer-than-content-length-error-for-delete-and-nocontent 
    (response_class=Response) is added to @router.delete with 204 status.
    """
    crud_user_role.deleteFamUserRoleAssignment(db, user_role_xref_id)
    LOGGER.debug(f"User/Role assignment deleted successfully, id: {user_role_xref_id}")
