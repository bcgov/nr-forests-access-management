import logging
import json
from urllib.request import urlopen

from .database import SessionLocal

LOGGER = logging.getLogger(__name__)


def get_db():
    try:
        LOGGER.debug("starting a new db session")
        db = SessionLocal()
        yield db

    except Exception:
        db.rollback()

    finally:
        db.commit()
        LOGGER.debug("closing db session")
        db.close()


def get_rsa_key_method():
    return get_rsa_key


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
