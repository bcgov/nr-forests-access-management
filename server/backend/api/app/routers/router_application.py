import logging
from typing import List
from api.app import database, schemas
from api.app.crud import crud_application
from api.app.routers.router_guards import authorize_by_app_id, get_current_requester
from api.app.schemas import Requester
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


LOGGER = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/{application_id}/user_role_assignment",
    response_model=List[schemas.FamApplicationUserRoleAssignmentGet],
    status_code=200,
    dependencies=[Depends(authorize_by_app_id)],  # Enforce application-level security
)
def get_fam_application_user_role_assignment(
    application_id: int,
    db: Session = Depends(database.get_db),
    requester: Requester = Depends(get_current_requester),
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
