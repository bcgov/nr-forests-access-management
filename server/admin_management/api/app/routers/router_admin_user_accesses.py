import logging

from api.app.jwt_validation import authorize
from api.app.routers.router_guards import get_current_requester
from api.app.routers.router_utils import admin_user_access_service_instance
from api.app.schemas import AdminUserAccessResponse, Requester
from api.app.services.admin_user_access_service import AdminUserAccessService
from fastapi import APIRouter, Depends

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    response_model=AdminUserAccessResponse,
    status_code=200,
    dependencies=[Depends(authorize)],
    name="Admin user access privilege",
    description="Admin access privilege/grants for logged on user.",
)
async def get_admin_user_access(
    requester: Requester = Depends(get_current_requester),  # Internally Requester already has basic token claim validated.
    admin_user_access_service: AdminUserAccessService = Depends(
        admin_user_access_service_instance),
):
    return admin_user_access_service.get_access_grants(requester.user_id)