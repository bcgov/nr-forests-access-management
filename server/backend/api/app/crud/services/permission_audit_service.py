import logging

from api.app.repositories.permission_audit_repository import \
    PermissionAuditRepository
from api.app.schemas.permission_audit_history import \
    PermissionAuditHistoryResDto
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)


class PermissionAuditService:

    def __init__(self, db: Session):
        self.repo = PermissionAuditRepository(db)

    def save(item: PermissionAuditHistoryResDto):
        pass
