from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field
from ...constants import (
    USER_NAME_MAX_LEN,
    ROLE_NAME_MAX_LEN,
    ROLE_DISPLAY_NAME_MAX_LEN,
    CLIENT_NUMBER_MAX_LEN,
)


class ExtUserRoleMetadataRoleSchema(BaseModel):
    """
    Schema for a single role in the user role metadata response.
    Represents a role assigned to a user with its expiry date and optional forest client association.
    """
    role_name: str = Field(
        description="The role name code (e.g., 'FOM_REVIEWER', 'SILVA_ADMIN')",
        max_length=ROLE_NAME_MAX_LEN,
    )
    display_name: Optional[str] = Field(
        default=None,
        description="Human-readable display name for the role",
        max_length=ROLE_DISPLAY_NAME_MAX_LEN,
    )
    expiry_date: Optional[datetime] = Field(
        default=None,
        description="UTC-aware ISO 8601 timestamp when the role assignment expires. NULL means no expiry.",
    )
    forest_client_number: Optional[str] = Field(
        default=None,
        description="Forest client number (e.g., '00001011') when the role is scoped to a forest client. NULL otherwise.",
        max_length=CLIENT_NUMBER_MAX_LEN,
    )

    model_config = ConfigDict(from_attributes=True)


class ExtUserRoleMetadataResponseSchema(BaseModel):
    """
    Response schema for /me/role-metadata endpoint.
    Returns the current JWT user's roles and their expiry metadata scoped to the requesting application.
    """
    user_name: str = Field(
        description="The authenticated user's username (e.g., 'JSMITH')",
        max_length=USER_NAME_MAX_LEN,
    )
    roles: List[ExtUserRoleMetadataRoleSchema] = Field(
        default_factory=list,
        description="List of roles assigned to the user in the application context. Empty list if no roles.",
    )

    model_config = ConfigDict(from_attributes=True)
