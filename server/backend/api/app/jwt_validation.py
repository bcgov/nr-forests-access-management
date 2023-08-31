import json
import logging
from http import HTTPStatus
from urllib.request import urlopen

from api.app import database
from api.app.constants import COGNITO_USERNAME_KEY
from api.app.crud import crud_application, crud_role, crud_user, crud_user_role
from api.app.models.model import FamUser, FamUserType
from api.app.schemas import Requester
# think that just importing config then access through its namespace makes code
# easier to understand, ie:
# import config
# then
# config.get_aws_region()
from api.config.config import (get_aws_region, get_oidc_client_id,
                               get_user_pool_domain_name, get_user_pool_id)
from fastapi import Depends, HTTPException, Request
from fastapi.params import Path
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import jwt
from requests import JSONDecodeError, request
from sqlalchemy.orm import Session

JWT_GROUPS_KEY = "cognito:groups"
JWT_CLIENT_ID_KEY = "client_id"

LOGGER = logging.getLogger(__name__)

ERROR_TOKEN_DECODE = "invalid_token_cannot_be_decoded"
ERROR_INVALID_CLIENT = "invalid_oidc_client"
ERROR_INVALID_ALGORITHM = "invalid_algorithm"
ERROR_MISSING_KID = "invalid_header_no_kid"
ERROR_NO_RSA_KEY = "invalid_token_no_rsa_key_match"
ERROR_EXPIRED_TOKEN = "invalid_token_expired"
ERROR_CLAIMS = "invalid_token_claims"
ERROR_VALIDATION = "validation_failed"
ERROR_GROUPS_REQUIRED = "authorization_groups_required"
ERROR_PERMISSION_REQUIRED = "permission_required_for_operation"
ERROR_INVALID_APPLICATION_ID = "invalid_application_id"
ERROR_INVALID_ROLE_ID = "invalid_role_id"

aws_region = get_aws_region()
user_pool_id = get_user_pool_id()
user_pool_domain_name = get_user_pool_domain_name()

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://{user_pool_domain_name}.auth.{aws_region}.amazoncognito.com/authorize",
    tokenUrl=f"https://{user_pool_domain_name}.auth.{aws_region}.amazoncognito.com/token",
    scopes=None,
    scheme_name=get_oidc_client_id(),
    auto_error=True,
)

_jwks = None


def init_jwks():
    global _jwks

    LOGGER.debug(
        f"Requesting aws jwks with region {aws_region} and user pood id {user_pool_id}..."
    )
    try:
        e = f"https://cognito-idp.{aws_region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json"
        with urlopen(e) as response:
            _jwks = json.loads(response.read().decode("utf-8"))

    except Exception as e:
        LOGGER.error(f"init_jwks function failed to reach AWS: {e}.")
        LOGGER.error("Backend API will not work properly.")
        raise e


def get_rsa_key_method():
    return get_rsa_key


def get_rsa_key(kid):

    global _jwks
    if not _jwks:
        init_jwks()

    """Return the matching RSA key for kid, from the jwks array."""
    rsa_key = {}
    for key in _jwks["keys"]:
        if key["kid"] == kid:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"],
            }
            break
    return rsa_key


def validate_token(
    token: str = Depends(oauth2_scheme),
    get_rsa_key_method: callable = Depends(get_rsa_key_method),
) -> dict:

    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail={
                "code": ERROR_TOKEN_DECODE,
                "description": "Unable to decode token.",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    if unverified_header["alg"] != "RS256":
        raise HTTPException(
            status_code=401,
            detail={
                "code": ERROR_INVALID_ALGORITHM,
                "description": "Invalid header. "
                "Use an RS256 signed JWT Access Token",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    if "kid" not in unverified_header:
        LOGGER.debug("Caught exception 'kid' not in header")
        raise HTTPException(
            status_code=401,
            detail={
                "code": ERROR_MISSING_KID,
                "description": "Invalid header. " "No KID in token header",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    rsa_key = get_rsa_key_method(unverified_header["kid"])

    if not rsa_key:
        LOGGER.debug("Caught exception rsa key not found")
        raise HTTPException(
            status_code=401,
            detail={
                "code": ERROR_NO_RSA_KEY,
                "description": "Invalid header. "
                "Unable to find jwks key referenced in token",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    aws_region = get_aws_region()
    user_pool_id = get_user_pool_id()

    try:
        jwt.decode(
            token,
            rsa_key,
            algorithms="RS256",
            issuer=f"https://cognito-idp.{aws_region}.amazonaws.com/{user_pool_id}",
        )

    except jwt.ExpiredSignatureError:
        LOGGER.debug("Caught exception jwt expired")
        raise HTTPException(
            status_code=401,
            detail={"code": ERROR_EXPIRED_TOKEN, "description": "Token has expired"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTClaimsError as err:
        raise HTTPException(
            status_code=401,
            detail={"code": ERROR_CLAIMS, "description": err.args[0]},
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(
            status_code=401,
            detail={"code": ERROR_VALIDATION, "description": "Unable to validate JWT"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    claims = jwt.get_unverified_claims(token)

    if claims[JWT_CLIENT_ID_KEY] != get_oidc_client_id():
        raise HTTPException(
            status_code=401,
            detail={
                "code": ERROR_INVALID_CLIENT,
                "description": "Incorrect client ID.",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    return claims


def authorize(claims: dict = Depends(validate_token)) -> dict:

    if JWT_GROUPS_KEY not in claims or len(claims[JWT_GROUPS_KEY]) == 0:
        raise HTTPException(
            status_code=403,
            detail={
                "code": ERROR_GROUPS_REQUIRED,
                "description": "At least one group required int cognito:groups claim",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    return claims


def authorize_by_app_id(
    application_id,
    db: Session = Depends(database.get_db),
    claims: dict = Depends(validate_token)
):
    application = crud_application.get_application(application_id=application_id, db=db)
    if not application:
        raise HTTPException(
            status_code=403,
            detail={
                "code": ERROR_INVALID_APPLICATION_ID,
                "description": f"Application ID {application_id} not found",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    required_role = f"{application.application_name.upper()}_ACCESS_ADMIN"
    access_roles = get_access_roles(claims)

    if required_role not in access_roles:
        raise HTTPException(
            status_code=403,
            detail={
                "code": ERROR_PERMISSION_REQUIRED,
                "description": f"Operation requires role {required_role}",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_request_role_id(
        request: Request,
        db: Session = Depends(database.get_db)
) -> int:
    """
    To get role id from request... (this is sub-dependency)
    Some endpoints has path_params with "user_role_xref_id".
    Some endpoints has role_id in request body.
    """
    user_role_xref_id = None
    if "user_role_xref_id" in request.path_params:
        user_role_xref_id = request.path_params["user_role_xref_id"]

    if (user_role_xref_id):
        user_role = crud_user_role.find_by_id(db, user_role_xref_id)
        return user_role.role_id

    else:
        try:
            rbody = await request.json()
            return rbody["role_id"]
        except JSONDecodeError:
            return None

def authorize_by_application_role(
    # provide role_id argument, if not present, default to Depends
    # (from Request "Body" object with "role_id" attribute).
    role_id: int = Depends(get_request_role_id),
    db: Session = Depends(database.get_db),
    claims: dict = Depends(validate_token),
):
    """
    This router validation is currently design to validate logged on "admin"
    has authority to perform actions for application with roles in [app]_ACCESS_ADMIN.
    This function basically is the same and depends on (authorize_by_app_id()) but for
    the need that some routers contains target role_id in the request (instead of application_id).
    """
    role = crud_role.get_role(db, role_id)
    if not role:
        raise HTTPException(
            status_code=403,
            detail={
                "code": ERROR_INVALID_ROLE_ID,
                "description": f"Role ID {role_id} not found",
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    authorize_by_app_id(
        application_id=role.application_id,
        db=db,
        claims=claims
    )
    return role


def get_access_roles(claims: dict = Depends(authorize)):
    groups = claims[JWT_GROUPS_KEY]
    return groups


def get_request_cognito_user_id(claims: dict = Depends(authorize)):
    # This is NOT user's name, display name or user ID.
    # It is mapped to "cognito:username" (ID Token) and "username" (Access Token).
    # It is the "cognito_user_id" column for fam_user table.
    # Example value: idir_b5ecdb094dfb4149a6a8445a0mangled0@idir
    cognito_username = claims[COGNITO_USERNAME_KEY]
    LOGGER.debug(f"Current requester's cognito_username for API: {cognito_username}")
    return cognito_username


async def get_current_requester(
    request_cognito_user_id: str = Depends(get_request_cognito_user_id),
    access_roles = Depends(get_access_roles),
    db: Session = Depends(database.get_db)
):
    fam_user: FamUser = crud_user.get_user_by_cognito_user_id(db, request_cognito_user_id)
    if fam_user is None:
        raise no_requester_exception

    requester = {
        "cognito_user_id": request_cognito_user_id,
        "user_name": fam_user.user_name,
        "user_type": fam_user.user_type_code,
        "access_roles": access_roles
    }

    LOGGER.debug(f"Current request user (requester): {requester}")
    return Requester(**requester)


def enforce_self_grant_guard_objects(
    db: Session = Depends(database.get_db),
    requester: Requester = Depends(get_current_requester)
):
    pass


ERROR_REQUESTER_NOT_EXISTS = "requester_not_exists"
no_requester_exception = HTTPException(
    status_code=HTTPStatus.FORBIDDEN, # 403
    detail={
        "code": ERROR_REQUESTER_NOT_EXISTS,
        "description": "Requester does not exist, action is not allowed",
    }
)


ERROR_EXTERNAL_USER_ACTION_PROHIBITED = "external_user_action_prohibited"


external_user_prohibited_exception = HTTPException(
    status_code=HTTPStatus.FORBIDDEN, # 403
    detail={
        "code": ERROR_EXTERNAL_USER_ACTION_PROHIBITED,
        "description": "Action is not allowed for external user.",
    }
)


async def internal_only_action(
    requester=Depends(get_current_requester)
):
    if requester.user_type is not FamUserType.USER_TYPE_IDIR:
        raise external_user_prohibited_exception