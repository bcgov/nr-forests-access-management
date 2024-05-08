import logging
from typing import List
from api.app import database, jwt_validation, schemas
from api.app.crud import crud_application
from api.app.routers.router_guards import authorize_by_app_id, get_current_requester
from api.app.schemas import Requester
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=List[schemas.FamApplication], status_code=200)
def get_applications(
    # response: Response,
    db: Session = Depends(database.get_db),
    access_roles: dict = Depends(jwt_validation.get_access_roles)
):

    """
    List of different applications that are administered by FAM
    """
    LOGGER.debug(f"running router ... {db}")
    query_data = crud_application.get_applications_by_granted_apps(db, access_roles)

    # from fastapi v0.79.0, setting status_code to 204, 304, or any code below 200 (1xx) will remove the body from the response
    # so when return response with status code 204, response will have no content return to user
    # if we want to use status code 204 for empty case, we might want to apply to other methods as well
    # and it will impact some test cases, casue the response cannot be conver to json in empty case

    # if len(query_data) == 0:
    #     response.status_code = 204

    return query_data


@router.get(
    "/{application_id}/fam_roles",
    response_model=List[schemas.FamApplicationRole],
    status_code=200,
    dependencies=[Depends(authorize_by_app_id)] # Enforce application-level security
)
def get_fam_application_roles(
    application_id: int,
    db: Session = Depends(database.get_db),
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
    dependencies=[Depends(authorize_by_app_id)] # Enforce application-level security
)
def get_fam_application_user_role_assignment(
    application_id: int,
    db: Session = Depends(database.get_db),
    requester: Requester = Depends(get_current_requester)
):
    """
    gets the roles assignment associated with an application
    """
    LOGGER.debug(f"Loading application role assigments for application_id: {application_id}")
    app_user_role_assignment = crud_application.get_application_role_assignments(
        db=db,
        application_id=application_id,
        requester=requester
    )
    LOGGER.debug(f"Completed loading application role assigments -\
                 # of results = {len(app_user_role_assignment)}")

    return app_user_role_assignment
