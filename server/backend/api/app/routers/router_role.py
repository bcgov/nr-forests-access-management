import logging
from typing import List

from api.app.crud import crud_role
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import database, schemas

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=List[schemas.FamRoleGet])
def get_fam_roles(db: Session = Depends(database.get_db)):
    """
    List of different roles that are administered by FAM
    """

    raise HTTPException(
        status_code=501,
        detail={'code': 'not_implemented',
                'description': 'This endpoint is not yet implemented'}
    )
    # LOGGER.debug(f"running router ... {db}")
    # query_data = crud_role.get_roles(db)
    # return query_data


@router.post("", response_model=schemas.FamRoleGet)
def create_fam_role(
    fam_role: schemas.FamRoleCreate, db: Session = Depends(database.get_db)
):
    """
    Add a role to FAM
    """

    raise HTTPException(
        status_code=501,
        detail={'code': 'not_implemented',
                'description': 'This endpoint is not yet implemented'}
    )

    # query_data = None
    # LOGGER.debug(f"running router ... {db}")
    # try:
    #     query_data = crud_role.create_role(fam_role, db)
    #     LOGGER.debug(f"query_data: {query_data}")
    # except IntegrityError as e:
    #     LOGGER.debug(f"error: {e}")
    #     raise HTTPException(status_code=422, detail=str(e))

    # return query_data
