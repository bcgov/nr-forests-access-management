import logging
from typing import List

from api.app import database, schemas
from api.app.routers.router_guards import authorize_by_fam_admin
from api.app.services.application_service import ApplicationService
from fastapi import APIRouter, Depends
from requests import Session
from typing_extensions import Annotated

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    response_model=List[schemas.FamApplicationGet],
    status_code=200,
    dependencies=[Depends(authorize_by_fam_admin)],
)
async def get_applications(
    db: Session = Depends(database.get_db),
):
    application_service = ApplicationService(db)
    return application_service.get_applications()
