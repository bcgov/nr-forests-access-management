import logging
from jose import jwt
from fastapi import HTTPException
import json
from urllib.request import urlopen

LOGGER = logging.getLogger(__name__)

ERROR_TOKEN_DECODE = "invalid_token_cannot_be_decoded"
ERROR_INVALID_CLIENT = "invalid_oidc_client"
ERROR_INVALID_ALGORITHM = "invalid_algorithm"
ERROR_MISSING_KID = "invalid_header_no_kid"
ERROR_NO_RSA_KEY = "invalid_token_no_rsa_key_match"
ERROR_EXPIRED_TOKEN = "invalid_token_expired"
ERROR_CLAIMS = "invalid_token_claims"
ERROR_VALIDATION = "validation_failed"


def get_rsa_key(kid):

    jsonurl = urlopen("https://cognito-idp.ca-central-1.amazonaws.com/ca-central-1_5BOn4rGL8/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read().decode('utf-8'))

    """Return the matching RSA key for kid, from the jwks array."""
    rsa_key = {}
    for key in jwks['keys']:
        if key['kid'] == kid:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    return rsa_key


def validate_token(token, get_rsa_key_method):

    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail={'code': ERROR_TOKEN_DECODE,
                    'description':
                        'Unable to decode token.'},
            headers={"WWW-Authenticate": "Bearer"},
        )
    if unverified_header['alg'] != 'RS256':
        raise HTTPException(
            status_code=401,
            detail={'code': ERROR_INVALID_ALGORITHM,
                    'description':
                        'Invalid header. '
                        'Use an RS256 signed JWT Access Token'},
            headers={"WWW-Authenticate": "Bearer"},
        )
    if 'kid' not in unverified_header:
        LOGGER.debug("Caught exception 'kid' not in header")
        raise HTTPException(
            status_code=401,
            detail={'code': ERROR_MISSING_KID,
                    'description':
                        'Invalid header. '
                        'No KID in token header'},
            headers={"WWW-Authenticate": "Bearer"},
        )

    rsa_key = get_rsa_key_method(unverified_header['kid'])

    if not rsa_key:
        LOGGER.debug("Caught exception rsa key not found")
        raise HTTPException(
            status_code=401,
            detail={'code': ERROR_NO_RSA_KEY,
                    'description':
                        'Invalid header. '
                        'Unable to find jwks key referenced in token'},
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        jwt.decode(
            token,
            rsa_key,
            algorithms='RS256',
            issuer="https://cognito-idp.ca-central-1.amazonaws.com/ca-central-1_5BOn4rGL8"
        )

    except jwt.ExpiredSignatureError:
        LOGGER.debug("Caught exception jwt expired")
        raise HTTPException(
            status_code=401,
            detail={'code': ERROR_EXPIRED_TOKEN,
                    'description': 'Token has expired'},
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTClaimsError as err:
        raise HTTPException(
            status_code=401,
            detail={'code': ERROR_CLAIMS,
                    'description': err.args[0]},
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(
            status_code=401,
            detail={'code': ERROR_VALIDATION,
                    'description': 'Unable to validate JWT'},
            headers={"WWW-Authenticate": "Bearer"},
        )

    claims = jwt.get_unverified_claims(token)

    if claims['client_id'] != "26tltjjfe7ktm4bte7av998d78":
        raise HTTPException(
            status_code=401,
            detail={'code': ERROR_INVALID_CLIENT,
                    'description': 'Incorrect client ID.'},
            headers={"WWW-Authenticate": "Bearer"},
        )

    return claims