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
    client_number: str = Query(min_length=8, max_length=8)
):
    """
    Forest Client(s) search (by defined query parameter(s)).

    param: 'client_number=[query_value]'
           Note! Current Forest Client API limits it to exact search for a whole 8-digits number.

    return: List of found FamForestClient. However, currently only 1 exact match returns.
    """
    LOGGER.debug(f"Searching Forest Clients with parameter client_number: {client_number}")
    forest_clients = crud_forest_client.search(client_number)
    LOGGER.debug(f"Returning {0 if forest_clients is None else len(forest_clients)} result.")
    return forest_clients

