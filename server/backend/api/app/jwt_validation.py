import logging
from jose import jwt
from fastapi import HTTPException

LOGGER = logging.getLogger(__name__)


def validate_token(token, get_rsa_key_method):

    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.JWTError:
        LOGGER.debug("Caught exception jwt.JWTError")
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if unverified_header['alg'] != 'RS256':
        LOGGER.debug("Caught exception unverified header")
        raise HTTPException(
            status_code=401,
            detail={'code': 'invalid_header',
                            'description':
                                'Invalid header. '
                                'Use an RS256 signed JWT Access Token'},
            headers={"WWW-Authenticate": "Bearer"},
        )
    if 'kid' not in unverified_header:
        LOGGER.debug("Caught exception 'kid' not in header")
        raise HTTPException(
            status_code=401,
            detail={'code': 'invalid_header',
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
            detail={'code': 'invalid_header',
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

        claims = jwt.get_unverified_claims(token)
        if claims['client_id'] != "26tltjjfe7ktm4bte7av998d78":
            raise HTTPException(
                status_code=401,
                detail={'code': 'invalid_claims',
                                'description':
                                    'Incorrect client ID. '
                                    'Please check the client_id'},
                headers={"WWW-Authenticate": "Bearer"},
            )

        return claims

    except jwt.ExpiredSignatureError:
        LOGGER.debug("Caught exception jwt expired")
        raise HTTPException(
            status_code=401,
            detail={'code': 'token_expired',
                            'description':
                                'Token expired. '
                                'Token has expired'},
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTClaimsError:
        LOGGER.debug("Caught exception incorrect issuer")
        raise HTTPException(
            status_code=401,
            detail={'code': 'invalid_claims',
                            'description':
                                'Incorrect issuer. '
                                'Please check the issuer'},
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        LOGGER.debug("Caught exception unknown error parsing jwt")
        raise HTTPException(
            status_code=401,
            detail={'code': 'invalid_header',
                            'description':
                                'Invalid header. '
                                'Unable to parse authentication'},
            headers={"WWW-Authenticate": "Bearer"},
        )