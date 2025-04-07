import logging
from typing import List

from api.app import database
from api.app.crud import crud_application, crud_user
from api.app.routers.router_guards import (
    authorize_by_app_id, enforce_bceid_terms_conditions_guard,
    get_current_requester)
from api.app.routers.router_utils import csv_file_data_streamer
from api.app.schemas import (FamApplicationUserRoleAssignmentGetSchema,
                             FamUserInfoSchema, RequesterSchema)
from api.app.schemas.pagination import (PagedResultsSchema,
                                        UserRolePageParamsSchema)
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
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
    application_id: int,
    db: Session = Depends(database.get_db),
    requester: RequesterSchema = Depends(get_current_requester),
    page_params: UserRolePageParamsSchema = Depends(),
):
    """
    Gets paged users/roles assignment records associated with an application.
    """
    LOGGER.debug(
        f"Loading application role assigments for application_id: {application_id}"
    )
    paged_results = crud_application.get_application_role_assignments(
        db=db, application_id=application_id, requester=requester, page_params=page_params
    )

    return paged_results


@router.get(
    "/{application_id}/user-role-assignment/export",
    dependencies=[
        Depends(authorize_by_app_id),
        Depends(enforce_bceid_terms_conditions_guard),
    ],
    summary="Export user roles information by application ID",
)
def export_application_user_roles(
    application_id: int,
    db: Session = Depends(database.get_db),
    requester: RequesterSchema = Depends(get_current_requester),
):
    """
    Export users/roles assignment records associated with an application as csv data
    """
    LOGGER.debug(
        f"Export users/roles assignment records associated with application_id: {application_id}"
    )
    results: List[FamApplicationUserRoleAssignmentGetSchema] = crud_application.get_application_role_assignments_no_paging(
        db=db, application_id=application_id, requester=requester
    )

    filename = f"application_{results[0].role.application.application_name}_user_roles.csv" if results else "user_roles.csv"
    return StreamingResponse(__export_app_user_roles_csv_file(results), media_type="text/csv", headers={
        "Access-Control-Expose-Headers":"Content-Disposition",
        "Content-Disposition": f"attachment; filename={filename}"
    })


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


def __export_app_user_roles_csv_file(data: List[FamApplicationUserRoleAssignmentGetSchema]):
    """
    This is a private helper function to export the user role assignment data to a CSV file.
    """
    ini_title_line = f"Application: {data[0].role.application.application_description}"
    csv_rows = [
        {
            "User Name": item.user.user_name,
            "Domain": item.user.user_type_relation.description,
            "First Name": item.user.first_name,
            "Last Name": item.user.last_name,
            "Email": item.user.email,
            "Forest Client ID": f"'{item.role.forest_client.forest_client_number}'" if item.role.forest_client else None,
            "Role": item.role.display_name,
            "Added On": item.create_date.strftime("%Y-%m-%d")
        } for item in data]
    return csv_file_data_streamer(ini_title_line=ini_title_line, data=csv_rows)
