import logging
from typing import List

from api.app.crud import crud_application
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from .. import dependencies, schemas

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=List[schemas.FamApplication], status_code=200)
def get_applications(response: Response, db: Session = Depends(dependencies.get_db)):
    """
    List of different applications that are administered by FAM
    """
    LOGGER.debug(f"running router ... {db}")
    query_data = crud_application.get_applications(db)
    if len(query_data) == 0:
        response.status_code = 204
    return query_data


@router.post("", response_model=schemas.FamApplication)
def create_application(
    application: schemas.FamApplicationCreate,
    db: Session = Depends(dependencies.get_db),
):
    """
    Add Application/client to FAM
    """
    LOGGER.debug(f"running router ... {db}")
    query_data = crud_application.create_application(application, db)
    return query_data


@router.delete("/{application_id}", response_model=schemas.FamApplication)
def delete_fam_application(
    application_id: int,
    db: Session = Depends(dependencies.get_db),
):
    """
    Add Application/client to FAM
    """
    LOGGER.debug(f"running router ... {db}")
    application = crud_application.get_application(application_id=application_id, db=db)
    if not application:
        raise HTTPException(
            status_code=404, detail=f"application_id={application_id} does not exist"
        )
    application_id = application.application_id
    LOGGER.debug(f"application_id: {application_id}")
    application = crud_application.delete_application(
        db=db, application_id=application_id
    )
    return application


@router.get(
    "/{application_id}/fam_roles",
    response_model=List[schemas.FamApplicationRole],
    status_code=200,
)
def get_fam_application_roles(
    application_id: int,
    db: Session = Depends(dependencies.get_db),
):
    """gets the roles associated with an application

    :param application_id: application id
    :param db: database session, defaults to Depends(dependencies.get_db)
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
)
def get_fam_application_user_role_assignment(
    application_id: int, db: Session = Depends(dependencies.get_db)
):
    """gets the roles associated with an application

    :param application_id: application id
    :param db: database session, defaults to Depends(dependencies.get_db)
    """
    LOGGER.debug(f"application_id: {application_id}")
    app_user_role_assignment = crud_application.get_application_role_assignments(
        db=db, application_id=application_id
    )
    LOGGER.debug(f"app_user_role_assignment: {app_user_role_assignment}")

    return app_user_role_assignment
