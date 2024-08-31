from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.declarative import DeclarativeMeta

# Create the Base and metadata objects
Base: DeclarativeMeta = declarative_base()
metadata = Base.metadata

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
