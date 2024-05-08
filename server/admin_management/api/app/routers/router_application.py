import logging
from typing import List

from api.app import schemas
from api.app.routers.router_guards import authorize_by_fam_admin
from api.app.routers.router_utils import application_service_instance
from api.app.services.application_service import ApplicationService
from fastapi import APIRouter, Depends

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    response_model=List[schemas.FamApplicationGetResponse],
    status_code=200,
    dependencies=[Depends(authorize_by_fam_admin)],
)
async def get_applications(
    application_service: ApplicationService = Depends(application_service_instance)
):
    return application_service.get_applications()
