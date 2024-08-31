from sqlalchemy.orm import configure_mappers
from .base import Base, metadata

from .fam_application import (
    FamApplicationModel,
    FamApplicationClientModel,
    FamAppEnvironmentModel,
)
from .fam_role import FamRoleModel, FamRoleTypeModel
from .fam_user import FamUserModel, FamUserTypeModel, FamUserTermsConditionsModel
from .fam_access_control import FamAccessControlPrivilegeModel
from .fam_forest_client import FamForestClientModel

# Ensure that all mappers are configured to avoid circular import issues
configure_mappers()

__all__ = [
    "Base",
    "metadata",
    "FamApplicationModel",
    "FamApplicationClientModel",
    "FamAppEnvironmentModel",
    "FamRoleModel",
    "FamRoleTypeModel",
    "FamUserModel",
    "FamUserTypeModel",
    "FamUserTermsConditionsModel",
    "FamAccessControlPrivilegeModel",
    "FamForestClientModel",
]
