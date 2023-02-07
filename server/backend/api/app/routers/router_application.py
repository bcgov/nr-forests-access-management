import logging

from typing import List
from api.app.crud import crud_application
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from .. import database, schemas, jwt_validation


LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=List[schemas.FamApplication], status_code=200)
def get_applications(
    response: Response,
    db: Session = Depends(database.get_db),
    access_roles: dict = Depends(jwt_validation.get_access_roles)
):

    """
    List of different applications that are administered by FAM
    """
    LOGGER.debug(f"running router ... {db}")
    query_data = crud_application.get_applications_by_granted_apps(db, access_roles)
    if len(query_data) == 0:
        response.status_code = 204
    return query_data


@router.get(
    "/{application_id}/fam_roles",
    response_model=List[schemas.FamApplicationRole],
    status_code=200,
)
def get_fam_application_roles(
    application_id: int,
    db: Session = Depends(database.get_db),
    token_claims: dict = Depends(jwt_validation.authorize)
):
    """gets the roles associated with an application

    :param application_id: application id
    :param db: database session, defaults to Depends(database.get_db)
    """

    # Enforce application-level security
    jwt_validation.authorize_by_app_id(application_id, db, token_claims)

    LOGGER.debug(f"Recieved application id: {application_id}")
    app_roles = crud_application.get_application_roles(
        application_id=application_id, db=db
    )
    return app_roles


@router.get(
    "/{application_id}/user_role_assignment",
    response_model=List[schemas.FamApplicationUserRoleAssignmentGet],
    status_code=200,
)
def get_fam_application_user_role_assignment(
    application_id: int,
    db: Session = Depends(database.get_db),
    token_claims: dict = Depends(jwt_validation.authorize)
):
    """gets the roles associated with an application

    :param application_id: application id
    :param db: database session, defaults to Depends(database.get_db)
    """

    # Enforce application-level security
    jwt_validation.authorize_by_app_id(application_id, db, token_claims)

    LOGGER.debug(f"Loading application role assigments for application_id: {application_id}")
    app_user_role_assignment = crud_application.get_application_role_assignments(
        db=db, application_id=application_id
    )
    LOGGER.debug(f"Finished loading application role assigments - # of results = {len(app_user_role_assignment)}")

    return app_user_role_assignment