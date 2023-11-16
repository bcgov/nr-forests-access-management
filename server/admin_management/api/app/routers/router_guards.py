import logging
from http import HTTPStatus
from fastapi import Depends, HTTPException

from api.app.jwt_validation import (
    ERROR_PERMISSION_REQUIRED,
    get_access_roles,
    validate_token,
)


LOGGER = logging.getLogger(__name__)


def authorize_by_fam_admin(claims: dict = Depends(validate_token)):
    required_role = "FAM_ACCESS_ADMIN"
    access_roles = get_access_roles(claims)

    if required_role not in access_roles:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail={
                "code": ERROR_PERMISSION_REQUIRED,
                "description": f"Operation requires role {required_role}",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
