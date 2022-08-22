import logging
from typing import List

from api.app.crud import crud_application, crud_role, crud_user
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import dependencies, schemas

LOGGER = logging.getLogger(__name__)

router = APIRouter()

@router.get("/fam_roles",
            response_model=List[schemas.FamRoleGet],
            tags=["FAM_roles"])
def get_fam_roles(db: Session = Depends(dependencies.get_db)):
    """
    List of different roles that are administered by FAM
    """
    LOGGER.debug(f"running router ... {db}")
    queryData = crud_role.getFamRoles(db)
    return queryData

@router.post("/fam_roles",
             response_model=schemas.FamRoleGet,
             tags=["FAM_roles"])
def create_fam_role(
    famRole: schemas.FamRole, db: Session = Depends(dependencies.get_db)
):
    """
    Add a role to FAM
    """
    queryData = None
    LOGGER.debug(f"running router ... {db}")
    try:
        queryData = crud_role.createFamRole(famRole, db)
        LOGGER.debug(f"queryData: {queryData}")
    except IntegrityError as e:
        LOGGER.debug(f"error: {e}")
        raise HTTPException(status_code=422, detail=str(e))

    return queryData
