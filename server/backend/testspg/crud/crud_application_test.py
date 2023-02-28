import time
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from api.app.crud import crud_application


def test_db(dbPgContainer, dbPgSession):
    dbPgContainer.start()
    time.sleep(5)  # wait db migration script to run
    query_data = crud_application.get_applications(dbPgSession)
    print('query_data', query_data)
    assert len(query_data) == 4
    dbPgSession.close()
    dbPgContainer.stop()
