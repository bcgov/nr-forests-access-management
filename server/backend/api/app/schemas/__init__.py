# --------------------------------- FAM Application --------------------------------- #
from .fam_application import FamApplicationSchema

# --------------------------------- FAM User --------------------------------- #
from .fam_user import FamUserSchema
from .fam_user_type import FamUserTypeSchema
from .fam_user_info import FamUserInfoSchema
from .fam_user_update_response import FamUserUpdateResponseSchema

# --------------------------------- FAM Forest Client--------------------------------- #
from .fam_forest_client_create import FamForestClientCreateSchema
from .fam_forest_client_status import FamForestClientStatusSchema
from .fam_forest_client import FamForestClientSchema

# --------------------------------- FAM Role--------------------------------- #
from .fam_role_create import FamRoleCreateSchema
from .fam_role_min import FamRoleMinSchema
from .fam_role_with_client import FamRoleWithClientSchema

# --------------------------------- FAM User Role Assignment--------------------------------- #
from .fam_user_role_assignment_create import FamUserRoleAssignmentCreateSchema
from .fam_application_user_role_assignment_get import (
    FamApplicationUserRoleAssignmentGetSchema,
)
from .fam_user_role_assignment_create_response import (
    FamUserRoleAssignmentCreateResponseSchema,
)
from .fam_user_role_assignment_response import FamUserRoleAssignmentResponseSchema

# ------------------------------------- IDIM Proxy API Integraion ---------------------------------------- #
from .idim_proxy_search_param import IdimProxySearchParamSchema
from .idim_proxy_bceid_search_param import IdimProxyBceidSearchParamSchema
from .idim_proxy_idir_info import IdimProxyIdirInfoSchema
from .idim_proxy_bceid_info import IdimProxyBceidInfoSchema

# ------------------------------------- GC Notify Integraion ---------------------------------------- #
from .gc_notify_grant_access_email_param import GCNotifyGrantAccessEmailParamSchema

# ------------------------------------- Forest Client API Integraion ---------------------------------------- #
from .forest_client_integration_find_response import (
    ForestClientIntegrationFindResponseSchema,
)


# ---------- System schema objects ---------- #
"""
The "Requester" and "TargetUser" schema objects are internal backend system
wide objects.
They are "NOT" intended as part of the request/respoinse body for endponts.
The "Requester" means "who" is issueing the request for one of FAM endpoints.
The "TargetUser" means "who" is the user this endpoint request is targeting
for.
    - The exsiting endpoints so far only target on one target user. It might be
      possible some endpoints will target on multiple users. In such case,
      further design or refactoring might be needed.
"""
from .requester import RequesterSchema
from .target_user import TargetUserSchema

# ---------- Permission Audit History Schemas ---------- #
from .privilege_details import PrivilegeDetailsSchema
from .change_user_detail import ChangeUserDetailsSchema