
import logging

from api.app import database
from api.app.services.access_control_privilege_service import \
    AccessControlPrivilegeService
from api.app.services.application_admin_service import ApplicationAdminService
from api.app.services.application_service import ApplicationService
from api.app.services.fam_admin_user_access_service import \
    FamAdminUserAccessService
from api.app.services.role_service import RoleService
from api.app.services.user_service import UserService
from fastapi import Depends
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)


# This is only use for router dependency on service instantiation.
# Might be imporved later for more generic for all similar services.
async def application_service_instance(
    db: Session = Depends(database.get_db),
) -> ApplicationService:
    application_service = ApplicationService(db)
    return application_service


async def application_admin_service_instance(
    db: Session = Depends(database.get_db),
) -> ApplicationAdminService:
    application_admin_service = ApplicationAdminService(db)
    return application_admin_service


async def user_service_instance(
    db: Session = Depends(database.get_db),
) -> UserService:
    user_service = UserService(db)
    return user_service


async def role_service_instance(
    db: Session = Depends(database.get_db),
) -> RoleService:
    role_service = RoleService(db)
    return role_service


async def access_control_privilege_service_instance(
    db: Session = Depends(database.get_db),
) -> AccessControlPrivilegeService:
    access_control_privilege_service = AccessControlPrivilegeService(db)
    return access_control_privilege_service


async def fam_admin_user_access_service_instance(
    db: Session = Depends(database.get_db),
) -> FamAdminUserAccessService:
    fam_admin_user_access_service = FamAdminUserAccessService(db)
    return fam_admin_user_access_service