import logging

from api.app.crud import crud_user_role
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import dependencies, schemas

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=schemas.FamUserRoleAssignmentGet
)
def create_user_role_assignment(
    userRoleAssignmentRequset: schemas.FamUserRoleAssignmentCreate,
    db: Session = Depends(dependencies.get_db),
):
    """
    Create FAM user_role_xref association.
    """
    LOGGER.debug(f"running router ... {db}")
    createData = crud_user_role.createFamUserRoleAssignment(
        userRoleAssignmentRequset,
        db
    )
    LOGGER.debug(f"User/Role assignment executed successfully, id: ${createData.user_role_xref_id}")
    return createData
