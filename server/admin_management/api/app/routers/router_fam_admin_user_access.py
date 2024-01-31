import logging

from api.app.jwt_validation import authorize
from api.app.routers.router_guards import get_current_requester
from api.app.routers.router_utils import fam_admin_user_access_service_instance
from api.app.schemas import Requester
from api.app.services.fam_admin_user_access_service import \
    FamAdminUserAccessService
from fastapi import APIRouter, Depends

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "",
    # response_model=List[FamApplicationGetResponse], ## TODO: schema to be decided.TODO and security checks
    status_code=200,
    dependencies=[Depends(authorize)],
    description="FAM admin user access privilege",
)
async def get_fam_admin_user_access(
    requester: Requester = Depends(get_current_requester),
    fam_admin_user_access_service: FamAdminUserAccessService = Depends(
        fam_admin_user_access_service_instance),
):
    return fam_admin_user_access_service.get_access_grants(requester.user_id)
