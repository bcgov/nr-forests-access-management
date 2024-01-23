
import logging

from api.app import database
from api.app.services.application_admin_service import ApplicationAdminService
from api.app.services.application_service import ApplicationService
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
