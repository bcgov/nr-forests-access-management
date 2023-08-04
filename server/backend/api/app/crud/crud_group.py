import datetime
import logging

from api.app.models import model as models
from sqlalchemy.orm import Session

from .. import schemas
from . import crud_utils as crud_utils

LOGGER = logging.getLogger(__name__)

# def createFamGroup(famGroup: schemas.FamGroupPost, db: Session):
#     """used to add a new FAM group to the database

#     :param famGroup: _description_
#     :type famGroup: schemas.FamGroupPost
#     :param db: _description_
#     :type db: Session
#     :return: _description_
#     :rtype: _type_
#     """
#     pkColName = crud_utils.get_primary_key(models.FamGroup)
#     nextVal = crud_utils.get_next(models.FamGroup, db)
#     famGroupDict = famGroup.dict()
#     famGroupDict[pkColName] = nextVal

#     now = datetime.datetime.now()
#     famGroupDict["create_date"] = now
#     famGroupDict["update_date"] = now

#     db_item = models.FamGroup(**famGroupDict)
#     db.add(db_item)
#     db.commit()
#     # db.refresh(db_item)
#     return db_item
