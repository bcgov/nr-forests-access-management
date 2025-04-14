import csv
import logging
from datetime import datetime
from io import StringIO
from typing import List

from api.app import database
from api.app.constants import ApiInstanceEnv
from api.app.crud import crud_application, crud_utils
from fastapi import Depends
from sqlalchemy.orm import Session

LOGGER = logging.getLogger(__name__)


def get_api_instance_env(
    application_id: int, db: Session = Depends(database.get_db)
) -> ApiInstanceEnv:
    application = crud_application.get_application(db, application_id)
    return crud_utils.use_api_instance_by_app(application)

async def csv_file_data_streamer(ini_title_line: str, data: List[dict[str, str]]):
    """
    This is a help function to stream data to a CSV file.
    Note: in this case, using 'yield' to stream the data to reduce memory usage.
    Arguments:
        ini_title_line: The title line in the CSV file.
        data: The data rows to be written to the CSV file.
    Returns:
        A generator that yields the CSV content.
    """
    # Add initial lines in memory for output
    initial_lines = f"Downloaded on: {datetime.now().strftime('%Y-%m-%d')}\n"
    csv_fields = data[0].keys() if data else []
    if data:
        initial_lines += f"{ini_title_line}\n"
    output = StringIO(initial_lines)
    yield output.getvalue()
    output.seek(0)
    output.truncate(0)

    fieldnames = [field for field in csv_fields]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.fieldnames = fieldnames
    writer.writeheader()
    yield output.getvalue()
    output.seek(0)
    output.truncate(0)

    # CSV content lines
    for row in data:
        writer.writerow(row)
        yield output.getvalue()
        output.seek(0)
        output.truncate(0)

    output.close()