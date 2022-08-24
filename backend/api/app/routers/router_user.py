import logging
from typing import List

from api.app.crud import crud_user
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import dependencies, schemas

LOGGER = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[schemas.FamUserGet])
def get_fam_users(db: Session = Depends(dependencies.get_db)):
    """
    List of different users that are administered by FAM
    """
    LOGGER.debug(f"running router ... {db}")
    queryData = crud_user.getFamUsers(db)
    return queryData

@router.post("/", response_model=schemas.FamUserGet)
def create_fam_user(
    famUser: schemas.FamUser, db: Session = Depends(dependencies.get_db)
):
    """
    Add a user to FAM
    """
    queryData = None
    LOGGER.debug(f"running router ... {db}")
    try:
        queryData = crud_user.createFamUser(famUser, db)
        LOGGER.debug(f"queryData: {queryData}")
    except IntegrityError as e:
        LOGGER.debug(f"error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    # except Exception as e:
    #     logging.debug("------ ERROR ------ ")
    #     logging.exception(e)

    return queryData

@router.delete(
    "/{user_id}", response_model=schemas.FamUser
)
def delete_fam_user(user_id: int, db: Session = Depends(dependencies.get_db)):
    """
    Delete a FAM user
    """

    user = crud_user.getFamUser(user_id=user_id, db=db)
    LOGGER.debug(f"user: {user}")
    if not user:
        raise HTTPException(status_code=404, detail=f"user_id={user_id} does not exist")
    user = crud_user.deleteUser(db=db, user_id=user_id)
    return user

@router.get(
    "/{user_id}", response_model=schemas.FamUserGet
)
def get_fam_user(user_id: int, db: Session = Depends(dependencies.get_db)):
    """
    Get a FAM user
    """
    LOGGER.debug(f"userid is: {user_id}")
    user = crud_user.getFamUser(user_id=user_id, db=db)
    LOGGER.debug(f"userdata: {user}")
    return user
