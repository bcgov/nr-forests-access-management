import json
import logging
from urllib.request import urlopen
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import jwt

from api.config.config import (get_aws_region, get_oidc_client_id,
                               get_user_pool_domain_name, get_user_pool_id)


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


def get_access_roles(claims: dict = Depends(authorize)):
    groups = claims[JWT_GROUPS_KEY]
    return groups