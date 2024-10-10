import logging

from api.app.models.model import FamPrivilegeChangeAudit
from api.app.schemas.permission_audit_history import \
    PermissionAuditHistoryCreateSchema
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)


class PermissionAuditRepository:

    def __init__(self, db: Session):
        self.db = db

    # --- Create ---

    def save(self, item: PermissionAuditHistoryCreateSchema) -> FamPrivilegeChangeAudit:
        db_item = FamPrivilegeChangeAudit(**item.model_dump())
        self.db.add(db_item)
        self.db.flush()
        return db_item
