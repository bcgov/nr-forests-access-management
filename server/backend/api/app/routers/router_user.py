import logging
from typing import List

from api.app.crud import crud_user
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import database, schemas

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=List[schemas.FamUserGet])
def get_users(db: Session = Depends(database.get_db)):
    """
    List of different users that are administered by FAM
    """

    raise HTTPException(
        status_code=501,
        detail={'code': 'not_implemented',
                'description': 'This endpoint is not yet implemented'}
    )

    # LOGGER.debug(f"running router ... {db}")
    # query_data = crud_user.get_users(db)
    # return query_data


@router.post("", response_model=schemas.FamUserGet)
def create_fam_user(
    famUser: schemas.FamUser, db: Session = Depends(database.get_db)
):
    """
    Add a user to FAM
    """

    raise HTTPException(
        status_code=501,
        detail={'code': 'not_implemented',
                'description': 'This endpoint is not yet implemented'}
    )

    # query_data = None
    # LOGGER.debug(f"running router ... {db}")
    # try:
    #     query_data = crud_user.create_user(famUser, db)
    #     LOGGER.debug(f"queryData: {query_data}")
    # except IntegrityError as e:
    #     LOGGER.debug(f"error: {e}")
    #     raise HTTPException(status_code=422, detail=str(e))

    # return query_data


@router.delete("/{user_id}", response_model=schemas.FamUser)
def delete_fam_user(user_id: int, db: Session = Depends(database.get_db)):
    """
    Delete a FAM user
    """

    raise HTTPException(
        status_code=501,
        detail={'code': 'not_implemented',
                'description': 'This endpoint is not yet implemented'}
    )

    # user = crud_user.get_user(user_id=user_id, db=db)
    # LOGGER.debug(f"user: {user}")
    # if not user:
    #     raise HTTPException(status_code=404, detail=f"user_id={user_id} does not exist")
    # user = crud_user.delete_user(db=db, user_id=user_id)
    # return user


@router.get("/{user_id}", response_model=schemas.FamUserGet)
def get_fam_user(user_id: int, db: Session = Depends(database.get_db)):

    """
    Get a FAM user
    """

    raise HTTPException(
        status_code=501,
        detail={'code': 'not_implemented',
                'description': 'This endpoint is not yet implemented'}
    )

    # LOGGER.debug(f"userid is: {user_id}")
    # user = crud_user.get_user(user_id=user_id, db=db)
    # LOGGER.debug(f"userdata: {user}")
    # return user
