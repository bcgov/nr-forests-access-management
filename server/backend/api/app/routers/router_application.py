import csv
import logging
from datetime import datetime
from enum import Enum
from io import StringIO
from typing import List

from api.app import database
from api.app.crud import crud_application, crud_user
from api.app.routers.router_guards import (
    authorize_by_app_id, enforce_bceid_terms_conditions_guard,
    get_current_requester)
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
    return StreamingResponse(__app_user_roles_csv_file_streamer(results), media_type="text/csv", headers={
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


async def __app_user_roles_csv_file_streamer(data: List[FamApplicationUserRoleAssignmentGetSchema]):
    """
    This is a private help function to stream the user role assignment data to a CSV file for use in
    router `export_application_user_roles()`.
    Note: in this case, using 'yield' to stream the data to reduce memory usage.
    """
    # Add initial lines in memory for output
    initial_lines = f"Downloaded on: {datetime.now().strftime('%Y-%m-%d')}\n"
    if data:
        initial_lines += f"Application: {data[0].role.application.application_description}\n"
    output = StringIO(initial_lines)
    yield output.getvalue()
    output.seek(0)
    output.truncate(0)

    # CSV header fields line
    class CSVFields(str, Enum):
        USER_NAME = "User Name"
        DOMAIN = "Domain"
        FIRST_NAME = "First Name"
        LAST_NAME = "Last Name"
        EMAIL = "Email"
        FOREST_CLIENT_ID = "Forest Client ID"
        ROLE_DISPLAY_NAME = "Role"
        ADDED_ON = "Added On"

    fieldnames = [field.value for field in CSVFields]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.fieldnames = fieldnames
    writer.writeheader()
    yield output.getvalue()
    output.seek(0)
    output.truncate(0)

    # CSV content lines
    for result in data:
        forest_client_number = f"'{result.role.forest_client.forest_client_number}'" if result.role.forest_client else None
        created_on = result.create_date.strftime("%Y-%m-%d")
        writer.writerow({
            CSVFields.USER_NAME: result.user.user_name,
            CSVFields.DOMAIN: result.user.user_type_relation.description,
            CSVFields.FIRST_NAME: result.user.first_name,
            CSVFields.LAST_NAME: result.user.last_name,
            CSVFields.EMAIL: result.user.email,
            CSVFields.FOREST_CLIENT_ID: forest_client_number,
            CSVFields.ROLE_DISPLAY_NAME: result.role.display_name,
            CSVFields.ADDED_ON: created_on
        })
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

    output.close()