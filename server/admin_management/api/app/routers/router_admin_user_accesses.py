import logging

from api.app.routers.router_guards import \
    get_current_requester_without_access_check
from api.app.routers.router_utils import admin_user_access_service_instance
from api.app.schemas.schemas import AdminUserAccessResponse, Requester
from api.app.services.admin_user_access_service import AdminUserAccessService
from fastapi import APIRouter, Depends

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    response_model=AdminUserAccessResponse,
    status_code=200,
    name="Admin user access privilege",
    description="Access privilege for logged on admin user for what applications/roles(scoped) the user can grant.",
)
async def get_admin_user_access(
    requester: Requester = Depends(
        get_current_requester_without_access_check
    ),  # the get_admin_user_access API don't require user has any access, it will return what access the user has
    admin_user_access_service: AdminUserAccessService = Depends(
        admin_user_access_service_instance
    ),
):
    return admin_user_access_service.get_access_grants(requester.user_id)
