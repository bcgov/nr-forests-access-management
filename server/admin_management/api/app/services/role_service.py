import logging
from sqlalchemy.orm import Session

from api.app import constants as famConstants
from api.app import schemas
from api.app.models import model as models
from api.app.repositories.role_repository import RoleRepository
from api.app.repositories.forest_client_repository import ForestClientRepository
from api.app.services.forest_client_service import ForestClientService


LOGGER = logging.getLogger(__name__)


class RoleService:
    def __init__(self, db: Session):
        self.role_repo = RoleRepository(db)
        self.forest_client_service = ForestClientService(db)
        self.forest_client_repository = ForestClientRepository(db)

    def get_role(self, role_id: int):
        return self.role_repo.get_role(role_id)

    def find_or_create_forest_client_child_role(
        self, forest_client_number: str, parent_role: models.FamRole, requester: str
    ):
        # find or create forest client number in the fam forest client table
        self.forest_client_service.find_or_create(forest_client_number, requester)

        forest_client_role_name = self.construct_forest_client_role_name(
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
                schemas.FamRoleCreate(
                    **{
                        "parent_role_id": parent_role.role_id,
                        "application_id": parent_role.application_id,
                        "forest_client_number": forest_client_number,
                        "role_name": forest_client_role_name,
                        "role_purpose": self.construct_forest_client_role_purpose(
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

    def create_role(self, role: schemas.FamRoleCreate) -> models.FamRole:
        LOGGER.debug(f"Creating Fam role: {role}")

        fam_role_dict = role.model_dump()
        forest_client_number = fam_role_dict["forest_client_number"]
        del fam_role_dict["forest_client_number"]

        # start by creating a role record
        fam_role_model = models.FamRole(**fam_role_dict)

        if forest_client_number:
            # need to create a forest client record

            # check if a forest client record already exists
            forest_client_record = self.forest_client_service.get_forest_client(
                forest_client_number
            )

            # if no forest client record is found then create one
            if not forest_client_record:
                LOGGER.debug("creating a forest client record")
                fc_dict = {
                    "forest_client_number": forest_client_number,
                    "client_name": "going to delete anyways when complete issue"
                    + f" 327 / {forest_client_number}",
                    "create_user": fam_role_model.create_user,
                }
                fc_pydantic = schemas.FamForestClientCreate(**fc_dict)
                forest_client_model = (
                    self.forest_client_repository.create_forest_client(
                        fam_forest_client=fc_pydantic
                    )
                )
                LOGGER.debug(
                    "forest client id: " + f"{forest_client_model.client_number_id}"
                )

                # finally add the forests client record to the role
                fam_role_model.client_number = forest_client_model
            else:
                fam_role_model.client_number = forest_client_record

        fam_role_model = self.role_repo.create_role(fam_role_model)
        return fam_role_model

    def construct_forest_client_role_name(
        self, parent_role_name: str, forest_client_number: str
    ):
        return f"{parent_role_name}_{forest_client_number}"

    def construct_forest_client_role_purpose(
        self, parent_role_purpose: str, forest_client_number: str
    ):
        client_purpose = f"{parent_role_purpose} for {forest_client_number}"
        return client_purpose