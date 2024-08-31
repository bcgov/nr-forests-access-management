from sqlalchemy.orm import configure_mappers

from .FamApplication import FamApplicationModel
from .FamForestClient import FamForestClientModel
from .FamAccessControlPrivilege import FamAccessControlPrivilegeModel
from .FamUserTermsConditions import FamUserTermsConditionsModel
from .FamUserType import FamUserTypeModel
from .FamUser import FamUserModel
from .FamApplicationClient import FamApplicationClientModel
from .FamRoleType import FamRoleTypeModel
from .FamRole import FamRoleModel
from .FamUserRoleXref import FamUserRoleXrefModel
from .FamAppEnvironment import FamAppEnvironmentModel

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
