import logging
import datetime
import starlette.testclient
from typing import Dict, Union, Iterator
from api.app.main import apiPrefix
import api.app.models.model as model
import sqlalchemy.orm.session

LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/fam_roles"


def test_post_fam_roles(
    test_client_fixture: starlette.testclient.TestClient,
    dbsession_application: sqlalchemy.orm.session.Session,
    application_dict: Iterator[Dict[str, Union[str, datetime.datetime]]],
) -> None:

    db = dbsession_application
    db.commit()
    application = (
        db.query(model.FamApplication)
        .filter(
            model.FamApplication.application_name
            == application_dict["application_name"] # NOSONAR
        )
        .one()
    )

    payload = {
        "role_name": "FOM_SUBMITTER_TESTING_00147611",
        "role_purpose": "fom role for forest client: 00147611",
        # "parent_role_id": 7,
        "application_id": application.application_id,
        "forest_client_number": "00147611",
        "create_user": "KC_MIGRATION",
        "role_type_code": "C",
    }

    response = test_client_fixture.post(f"{endPoint}", json=payload)
    data = response.json()
    LOGGER.debug(f"response code: {response.status_code}")
    LOGGER.debug(f"response data: {data}")
    assert data["application_id"] == payload["application_id"]
    assert data["role_name"] == payload["role_name"]
    assert data["create_user"] == payload["create_user"]
    assert (
        data["client_number"]["forest_client_number"] == payload["forest_client_number"]
    )
