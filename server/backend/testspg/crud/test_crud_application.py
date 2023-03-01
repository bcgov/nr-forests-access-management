import os
import sys
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from api.app.crud import crud_application


def test_get_applications(dbPgSession: sessionmaker):
    apps = crud_application.get_applications(db=dbPgSession)
    assert len(apps) == 4
    assert hasattr(apps[0], "application_name")
    assert apps[0].application_name == "FAM"


def test_get_application(dbPgSession: sessionmaker):
    apps = crud_application.get_applications(db=dbPgSession)
    assert len(apps) == 4
    for app in apps:
        app_by_id = crud_application.get_application(
            db=dbPgSession, application_id=app.application_id
        )
        assert app_by_id.application_id == app.application_id


def test_get_application_by_name(dbPgSession: sessionmaker):
    apps = crud_application.get_applications(db=dbPgSession)
    assert len(apps) == 4
    for app in apps:
        app_by_name = crud_application.get_application_by_name(
            db=dbPgSession, application_name=app.application_name
        )
        assert app_by_name.application_name == app.application_name
