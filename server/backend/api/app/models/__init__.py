from sqlalchemy.orm import configure_mappers

from .fam_application import FamApplicationModel
from .fam_forest_client import FamForestClientModel
from .fam_access_control_privilege import FamAccessControlPrivilegeModel
from .fam_user_terms_conditions import FamUserTermsConditionsModel
from .fam_user_type import FamUserTypeModel
from .fam_user import FamUserModel
from .fam_application_client import FamApplicationClientModel
from .fam_role_type import FamRoleTypeModel
from .fam_role import FamRoleModel
from .fam_user_role_xref import FamUserRoleXrefModel
from .fam_app_environment import FamAppEnvironmentModel

# Ensure all mappers are configured after all models have been imported
configure_mappers()

__all__ = [
    "FamApplicationModel",
    "FamForestClientModel",
    "FamAccessControlPrivilegeModel",
    "FamUserTermsConditionsModel",
    "FamUserTypeModel",
    "FamUserModel",
    "FamApplicationClientModel",
    "FamRoleTypeModel",
    "FamRoleModel",
    "FamUserRoleXrefModel",
    "FamAppEnvironmentModel",
]
