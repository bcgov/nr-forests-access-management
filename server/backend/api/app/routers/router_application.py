import logging
import json
from typing import List

from api.app.crud import crud_application
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2AuthorizationCodeBearer
from sqlalchemy.orm import Session
from jose import jwt
from urllib.request import urlopen

from .. import dependencies, schemas


LOGGER = logging.getLogger(__name__)

router = APIRouter()

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://dev-fam-user-pool-domain.auth.ca-central-1.amazoncognito.com/authorize",
    tokenUrl="https://dev-fam-user-pool-domain.auth.ca-central-1.amazoncognito.com/token",
    scopes=None,
    scheme_name='26tltjjfe7ktm4bte7av998d78',
    auto_error=True,
)


@router.get("", response_model=List[schemas.FamApplication], status_code=200)
def get_applications(response: Response, db: Session = Depends(dependencies.get_db), token: str = Depends(oauth2_scheme)):

    payload = _validate_token(token)
    LOGGER.debug(payload)

    """
    List of different applications that are administered by FAM
    """
    LOGGER.debug(f"running router ... {db}")
    query_data = crud_application.get_applications(db)
    if len(query_data) == 0:
        response.status_code = 204
    return query_data


@router.post("", response_model=schemas.FamApplication)
def create_application(
    application: schemas.FamApplicationCreate,
    db: Session = Depends(dependencies.get_db),
):
    """
    Add Application/client to FAM
    """
    LOGGER.debug(f"running router ... {db}")
    query_data = crud_application.create_application(application, db)
    return query_data


@router.delete("/{application_id}", response_model=schemas.FamApplication)
def delete_fam_application(
    application_id: int,
    db: Session = Depends(dependencies.get_db),
):
    """
    Add Application/client to FAM
    """
    LOGGER.debug(f"running router ... {db}")
    application = crud_application.get_application(application_id=application_id, db=db)
    if not application:
        raise HTTPException(
            status_code=404, detail=f"application_id={application_id} does not exist"
        )
    application_id = application.application_id
    LOGGER.debug(f"application_id: {application_id}")
    application = crud_application.delete_application(
        db=db, application_id=application_id
    )
    return application


@router.get(
    "/{application_id}/fam_roles",
    response_model=List[schemas.FamApplicationRole],
    status_code=200,
)
def get_fam_application_roles(
    application_id: int,
    db: Session = Depends(dependencies.get_db),
):
    """gets the roles associated with an application

    :param application_id: application id
    :param db: database session, defaults to Depends(dependencies.get_db)
    """
    LOGGER.debug(f"Recieved application id: {application_id}")
    app_roles = crud_application.get_application_roles(
        application_id=application_id, db=db
    )
    return app_roles


@router.get(
    "/{application_id}/user_role_assignment",
    response_model=List[schemas.FamApplicationUserRoleAssignmentGet],
    status_code=200,
)
def get_fam_application_user_role_assignment(
    application_id: int, db: Session = Depends(dependencies.get_db)
):
    """gets the roles associated with an application

    :param application_id: application id
    :param db: database session, defaults to Depends(dependencies.get_db)
    """
    LOGGER.debug(f"application_id: {application_id}")
    app_user_role_assignment = crud_application.get_application_role_assignments(
        db=db, application_id=application_id
    )
    LOGGER.debug(f"app_user_role_assignment: {app_user_role_assignment}")

    return app_user_role_assignment


def _validate_token(token):

    try:
        unverified_header = jwt.get_unverified_header(token)
    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if unverified_header['alg'] == 'HS256':
        raise HTTPException(
            status_code=401,
            detail={'code': 'invalid_header',
                            'description':
                                'Invalid header. '
                                'Use an RS256 signed JWT Access Token'},
            headers={"WWW-Authenticate": "Bearer"},
        )
    if 'kid' not in unverified_header:
        raise HTTPException(
            status_code=401,
            detail={'code': 'invalid_header',
                            'description':
                                'Invalid header. '
                                'No KID in token header'},
            headers={"WWW-Authenticate": "Bearer"},
        )

    rsa_key = _get_rsa_key(unverified_header['kid'])

    if not rsa_key:
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
        raise HTTPException(
            status_code=401,
            detail={'code': 'token_expired',
                            'description':
                                'Token expired. '
                                'Token has expired'},
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTClaimsError:
        raise HTTPException(
            status_code=401,
            detail={'code': 'invalid_claims',
                            'description':
                                'Incorrect issuer. '
                                'Please check the issuer'},
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(
            status_code=401,
            detail={'code': 'invalid_header',
                            'description':
                                'Invalid header. '
                                'Unable to parse authentication'},
            headers={"WWW-Authenticate": "Bearer"},
        )


def _get_rsa_key(kid):

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


