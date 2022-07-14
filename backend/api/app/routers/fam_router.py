import logging
import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session


from .. import crud, dependencies, schemas

LOGGER = logging.getLogger(__name__)

router = APIRouter()




@router.get("/fam_applications", response_model=list[schemas.FamApplication],
            tags=['FAM_application'])
def show_fam_applications(db: Session = Depends(dependencies.get_db)):
    """
    List of different applications that are administered by FAM
    """
    LOGGER.debug(f"running router ... {db}")
    queryData = crud.getFamApplications(db)
    return queryData

@router.post("/fam_applications", response_model=schemas.FamApplication,
            tags=['FAM_application'])
def create_fam_application(famApplication: schemas.FamApplicationCreate,
    db: Session = Depends(dependencies.get_db)):
    """
    Add Application/client to FAM
    """
    LOGGER.debug(f"running router ... {db}")
    queryData = crud.createFamApplication(famApplication, db)
    #return queryData
    return queryData

@router.get("/fam_users", response_model=list[schemas.FamUserGet],
            tags=['FAM_users'])
def show_fam_users(db: Session = Depends(dependencies.get_db)):
    """
    List of different applications that are administered by FAM
    """
    LOGGER.debug(f"running router ... {db}")
    queryData = crud.getFamUsers(db)
    return queryData

@router.post("/fam_users", response_model=schemas.FamUser,
            tags=['FAM_users'])
def create_fam_user(famUser: schemas.FamUser,
    db: Session = Depends(dependencies.get_db)):
    """
    Add a user to FAM
    """
    try:
        LOGGER.debug(f"running router ... {db}")
        queryData = crud.createFamUser(famUser, db)
        LOGGER.debug(f"queryData: {queryData}")
    except:
        logging.debug("------ ERROR ------ ")
        logging.exception()

    return queryData

@router.delete("/fam_users/{user_id}", response_model=schemas.FamUser,
            tags=['FAM_users'])
def delete_fam_user(user_id: int,
    db: Session = Depends(dependencies.get_db)):
    """
    Delete a FAM user
    """
    user = crud.getFamUser(user_id=user_id, db=db)
    if not user:
        raise HTTPException(status_code=404, detail=f"user_id={user_id} does not exist")
    user = crud.deleteUser(db=db, user_id=user_id)
    return user



