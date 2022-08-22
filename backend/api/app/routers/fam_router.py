import logging
from typing import List

from api.app.crud import crud_application, crud_role, crud_user
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import dependencies, schemas

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/fam_applications",
    response_model=List[schemas.FamApplication],
    tags=["FAM_application"],
    status_code=200
)
def get_fam_applications(response: Response,
                         db: Session = Depends(dependencies.get_db)):
    """
    List of different applications that are administered by FAM
    """
    LOGGER.debug(f"running router ... {db}")
    queryData = crud_application.getFamApplications(db)
    if len(queryData) == 0:
        response.status_code = 204
    return queryData


@router.post(
    "/fam_applications", response_model=schemas.FamApplication, tags=["FAM_application"]
)
def create_fam_application(
    famApplication: schemas.FamApplicationCreate,
    db: Session = Depends(dependencies.get_db),
):
    """
    Add Application/client to FAM
    """
    LOGGER.debug(f"running router ... {db}")
    queryData = crud_application.createFamApplication(famApplication, db)
    # return queryData
    return queryData


@router.delete(
    "/fam_applications/{application_id}",
    response_model=schemas.FamApplication,
    tags=["FAM_application"],
)
def delete_fam_application(
    application_id: int,
    db: Session = Depends(dependencies.get_db),
):
    """
    Add Application/client to FAM
    """
    LOGGER.debug(f"running router ... {db}")
    application = crud_application.getFamApplication(application_id=application_id, db=db)
    if not application:
        raise HTTPException(
            status_code=404, detail=f"application_id={application_id} does not exist"
        )
    application_id = application.application_id
    LOGGER.debug(f"application_id: {application_id}")
    application = crud_application.deleteFamApplication(db=db, application_id=application_id)
    return application


@router.get("/fam_users", response_model=List[schemas.FamUserGet], tags=["FAM_users"])
def get_fam_users(db: Session = Depends(dependencies.get_db)):
    """
    List of different users that are administered by FAM
    """
    LOGGER.debug(f"running router ... {db}")
    queryData = crud_user.getFamUsers(db)
    return queryData


@router.post("/fam_users", response_model=schemas.FamUserGet, tags=["FAM_users"])
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
    "/fam_users/{user_id}", response_model=schemas.FamUser, tags=["FAM_users"]
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
    "/fam_users/{user_id}", response_model=schemas.FamUserGet, tags=["FAM_users"]
)
def get_fam_user(user_id: int, db: Session = Depends(dependencies.get_db)):
    """
    Get a FAM user
    """
    LOGGER.debug(f"userid is: {user_id}")
    user = crud_user.getFamUser(user_id=user_id, db=db)
    LOGGER.debug(f"userdata: {user}")
    return user


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
