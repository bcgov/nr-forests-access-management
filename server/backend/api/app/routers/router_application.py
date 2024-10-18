import logging

from api.app import database
from api.app.crud import crud_application, crud_user
from api.app.routers.router_guards import (
    authorize_by_app_id, enforce_bceid_terms_conditions_guard,
    get_current_requester)
from api.app.schemas import (FamApplicationUserRoleAssignmentGetSchema,
                             FamUserInfoSchema, RequesterSchema)
from api.app.schemas.pagination import (PagedResultsSchema,
                                        UserRolePageParamsSchema)
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/{application_id}/user-role-assignment",
    response_model=PagedResultsSchema[FamApplicationUserRoleAssignmentGetSchema],
    status_code=200,
    dependencies=[
        Depends(authorize_by_app_id),  # Enforce application-level security
        Depends(enforce_bceid_terms_conditions_guard),
    ],
)
def get_fam_application_user_role_assignment(
    response: Response,
    application_id: int,
    db: Session = Depends(database.get_db),
    requester: RequesterSchema = Depends(get_current_requester),
    page_params: UserRolePageParamsSchema = Depends(),
):
    """

    Gets the users/roles assignment associated with an application
    """
    LOGGER.debug(
        f"Loading application role assigments for application_id: {application_id}"
    )
    paged_results = crud_application.get_application_role_assignments(
        db=db, application_id=application_id, requester=requester, page_params=page_params
    )
    response.headers["x-total-count"] = f"{paged_results.total}"
    return paged_results


@router.get(
    "/{application_id}/users/{user_id}",
    response_model=FamUserInfoSchema,
    status_code=200,
    dependencies=[Depends(authorize_by_app_id)],
    summary="Retrieve User Information by User ID under an application",
    responses={
        404: {
            "description": "User not found",
            "content": {"application/json": {"example": {"detail": "User not found"}}},
        }
    },
)
async def get_application_user_by_id(    user_id: int,
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
    user = crud_user.get_user(user_id=user_id, db=db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
