import logging
from typing import List

from api.app.jwt_validation import authorize
from api.app.routers.router_guards import get_current_requester
from api.app.routers.router_utils import fam_admin_user_access_service_instance
from api.app.schemas import FamAdminUserAccessResponse, Requester
from api.app.services.fam_admin_user_access_service import \
    FamAdminUserAccessService
from fastapi import APIRouter, Depends

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    response_model=FamAdminUserAccessResponse,
    status_code=200,
    dependencies=[Depends(authorize)],
    name="FAM admin user access privilege",
    description="FAM admin access privilege/grants for logged on user.",
)
async def get_fam_admin_user_access(
    requester: Requester = Depends(get_current_requester),  # Internally Requester already has basic token claim validated.
    fam_admin_user_access_service: FamAdminUserAccessService = Depends(
        fam_admin_user_access_service_instance),
):
    return fam_admin_user_access_service.get_access_grants(requester.user_id)
