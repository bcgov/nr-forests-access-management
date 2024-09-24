import logging
from typing import List

from api.app import database
from api.app.crud import crud_application, crud_user
from api.app.routers.router_guards import (
    authorize_by_app_id,
    enforce_bceid_terms_conditions_guard,
    get_current_requester,
)
from api.app.schemas import (
    FamApplicationUserRoleAssignmentGetSchema,
    RequesterSchema,
    FamUserInfoSchema,
)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


LOGGER = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/{application_id}/user_role_assignment",
    response_model=List[FamApplicationUserRoleAssignmentGetSchema],
    status_code=200,
    dependencies=[
        Depends(authorize_by_app_id),  # Enforce application-level security
        Depends(enforce_bceid_terms_conditions_guard),
    ],
)
def get_fam_application_user_role_assignment(
    application_id: int,
    db: Session = Depends(database.get_db),
    requester: RequesterSchema = Depends(get_current_requester),
):
    """
    gets the roles assignment associated with an application
    """
    LOGGER.debug(
        f"Loading application role assigments for application_id: {application_id}"
    )
    app_user_role_assignment = crud_application.get_application_role_assignments(
        db=db, application_id=application_id, requester=requester
    )
    LOGGER.debug(
        f"Completed loading application role assigments -\
                 # of results = {len(app_user_role_assignment)}"
    )
    return app_user_role_assignment


@router.get(
    "/{application_id}/users/{user_id}",
    response_model=FamUserInfoSchema,
    status_code=200,
    dependencies=[Depends(authorize_by_app_id)],
    summary="Retrieve User Information by User ID under an application",
)
async def get_user_by_user_id(
    user_id: int,
    db: Session = Depends(database.get_db),
):
    """
    Retrieve the user data for a given user id under an authorized application.

    Args:
        userId (int): The ID of the user.
        applicationId (int): The ID of the application the user has access to.

    Returns:
        FamUserInfoSchema: The user information corresponding to the provided userId.
    """
    return crud_user.get_user(user_id=user_id, db=db)
