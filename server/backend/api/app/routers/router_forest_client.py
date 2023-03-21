import logging
from typing import List

from api.app.crud import crud_forest_client
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import database, schemas

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.get("/search", response_model=List[schemas.FamForestClient])
def search(
    client_number: str = Query(min_length=3, max_length=8),
    db: Session = Depends(database.get_db)
):
    """
    Forest Client(s) search.
    Searching by defined query parameter(s):
    param: client_number: '?client_number=[query_value]'
    return:
    """
    LOGGER.debug(f"Searching Forest Clients with parameter client_number: {client_number}")
    forest_clients = crud_forest_client.search(db, client_number)
    LOGGER.debug(f"Returning {0 if forest_clients is None else forest_clients.length} result.")
    return forest_clients

