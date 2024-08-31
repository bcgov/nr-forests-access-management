from sqlalchemy.orm import declarative_base, configure_mappers
from sqlalchemy.ext.declarative import DeclarativeMeta

# Create the Base and metadata objects
Base: DeclarativeMeta = declarative_base()
metadata = Base.metadata

# Import models with fewer dependencies first

from .FamApplication import FamApplicationModel
from .FamForestClient import FamForestClientModel
from .FamAppEnvironment import FamAppEnvironmentModel

# Import models that have dependencies on previously imported models

from .FamRoleType import FamRoleTypeModel
from .FamUserType import FamUserTypeModel
from .FamRole import FamRoleModel
from .FamUser import FamUserModel

# Import models that depend on multiple others

from .FamAccessControlPrivilege import FamAccessControlPrivilegeModel
from .FamUserRoleXref import FamUserRoleXrefModel
from .FamUserTermsConditions import FamUserTermsConditionsModel
from .FamApplicationClient import FamApplicationClientModel

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
