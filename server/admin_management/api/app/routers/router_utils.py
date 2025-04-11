
import csv
import logging
from datetime import datetime
from io import StringIO
from typing import List

from api.app import database
from api.app.services.access_control_privilege_service import \
    AccessControlPrivilegeService
from api.app.services.admin_user_access_service import AdminUserAccessService
from api.app.services.application_admin_service import ApplicationAdminService
from api.app.services.application_service import ApplicationService
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


async def admin_user_access_service_instance(
    db: Session = Depends(database.get_db),
) -> AdminUserAccessService:
    admin_user_access_service = AdminUserAccessService(db)
    return admin_user_access_service


async def csv_file_data_streamer(ini_title_line: str, data: List[dict[str, str]]):
    """
    This is a help function to stream data to a CSV file.
    Note: in this case, using 'yield' to stream the data to reduce memory usage.
    Arguments:
        ini_title_line: The title line in the CSV file.
        data: The data rows to be written to the CSV file.
    Returns:
        A generator that yields the CSV content.
    """
    # Add initial lines in memory for output
    initial_lines = f"Downloaded on: {datetime.now().strftime('%Y-%m-%d')}\n"
    csv_fields = data[0].keys() if data else []
    if data:
        initial_lines += f"{ini_title_line}\n"
    output = StringIO(initial_lines)
    yield output.getvalue()
    output.seek(0)
    output.truncate(0)

    fieldnames = [field for field in csv_fields]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.fieldnames = fieldnames
    writer.writeheader()
    yield output.getvalue()
    output.seek(0)
    output.truncate(0)

    # CSV content lines
    for row in data:
        writer.writerow(row)
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

    output.close()