import logging
from sqlalchemy.orm import Session

from api.app import constants as famConstants
from api.app.utils import utils
from api.app.schemas import FamRoleCreate
from api.app.models.model import FamRole
from api.app.repositories.role_repository import RoleRepository
from api.app.repositories.forest_client_repository import ForestClientRepository
from api.app.services.forest_client_service import ForestClientService


LOGGER = logging.getLogger(__name__)


class RoleService:
    def __init__(self, db: Session):
        self.role_repo = RoleRepository(db)
        self.forest_client_service = ForestClientService(db)
        self.forest_client_repository = ForestClientRepository(db)

    def get_role_by_id(self, role_id: int):
        return self.role_repo.get_role_by_id(role_id)

    def find_or_create_forest_client_child_role(
        self, forest_client_number: str, parent_role: FamRole, requester: str
    ):
        forest_client_role_name = utils.construct_forest_client_role_name(
            parent_role.role_name, forest_client_number
        )

        # Verify if Forest Client role (child role) exist
        child_role = self.role_repo.get_role_by_role_name_and_app_id(
            forest_client_role_name, parent_role.application_id
        )
        LOGGER.debug(
            "Forest Client child role for role_name "
            f"'{forest_client_role_name}':"
            f" {'Does not exist' if not child_role else 'Exists'}"
        )

        if not child_role:
            child_role = self.create_role(
                FamRoleCreate(
                    **{
                        "parent_role_id": parent_role.role_id,
                        "application_id": parent_role.application_id,
                        "forest_client_number": forest_client_number,
                        "role_name": forest_client_role_name,
                        "role_purpose": utils.construct_forest_client_role_purpose(
                            parent_role_purpose=parent_role.role_purpose,
                            forest_client_number=forest_client_number,
                        ),
                        "create_user": requester,
                        "role_type_code": famConstants.RoleType.ROLE_TYPE_CONCRETE,
                    }
                ),
            )
            LOGGER.debug(
                f"Child role {child_role.role_id} added for parent role "
                f"{parent_role.role_name}({child_role.parent_role_id})."
            )
        return child_role

    def create_role(self, role: FamRoleCreate) -> FamRole:
        LOGGER.debug(f"Creating Fam role: {role}")

        forest_client_number = role["forest_client_number"]
        del role["forest_client_number"]

        if forest_client_number:
            # find or create forest client number in the fam forest client table
            forest_client_record = self.forest_client_service.find_or_create(
                forest_client_number, role.get("create_user")
            )
            role["client_number"] = forest_client_record

        fam_role_model = self.role_repo.create_role(role)
        return fam_role_model