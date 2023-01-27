import logging
from typing import List

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from api.app.crud import crud_application
from api.app.jwt_validation import authorize_by_app_id

from .. import database, schemas

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=List[schemas.FamApplication], status_code=200)
def get_applications(
    response: Response,
    db: Session = Depends(database.get_db)
):
    """
    List of different applications that are administered by FAM
    """
    LOGGER.debug(f"running router ... {db}")
    query_data = crud_application.get_applications(db)
    if len(query_data) == 0:
        response.status_code = 204
    return query_data


@router.get(
    "/{application_id}/fam_roles",
    response_model=List[schemas.FamApplicationRole],
    status_code=200,
    dependencies=[Depends(authorize_by_app_id)]
)
def get_fam_application_roles(
    application_id: int,
    db: Session = Depends(database.get_db)
):
    """gets the roles associated with an application

    :param application_id: application id
    :param db: database session, defaults to Depends(database.get_db)
    """

    LOGGER.debug(f"Recieved application id: {application_id}")
    app_roles = crud_application.get_application_roles(
        application_id=application_id, db=db
    )
    return app_roles


@router.get(
    "/{application_id}/user_role_assignment",
    response_model=List[schemas.FamApplicationUserRoleAssignmentGet],
    status_code=200,
    dependencies=[Depends(authorize_by_app_id)]
)
def get_fam_application_user_role_assignment(
    application_id: int,
    db: Session = Depends(database.get_db)
):
    """gets the roles associated with an application

    :param application_id: application id
    :param db: database session, defaults to Depends(database.get_db)
    """

    LOGGER.debug(f"application_id: {application_id}")
    app_user_role_assignment = crud_application.get_application_role_assignments(
        db=db, application_id=application_id
    )
    LOGGER.debug(f"app_user_role_assignment: {app_user_role_assignment}")

    return app_user_role_assignment