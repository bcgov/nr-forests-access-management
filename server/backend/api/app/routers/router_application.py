import logging
from typing import List

from api.app.crud import crud_application
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from .. import dependencies, schemas

LOGGER = logging.getLogger(__name__)

router = APIRouter()

# @router.get(
#     "/",
#     response_model=List[schemas.FamApplication],
#     status_code=200
# )
@router.get(
    "",
    response_model=List[schemas.FamApplication],
    status_code=200
)
@router.get(
    "",
    response_model=List[schemas.FamApplication],
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
    "", response_model=schemas.FamApplication
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
    "/{application_id}",
    response_model=schemas.FamApplication
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
