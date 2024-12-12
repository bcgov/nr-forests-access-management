import logging.config
import os.path

from api.app.exception_handlers import (requests_http_error_handler,
                                        unhandled_exception_handler,
                                        validation_exception_handler)
from api.app.routers import (router_access_control_privilege,
                             router_admin_user_accesses,
                             router_application_admin, router_smoke_test)
from api.config.config import get_allow_origins, get_root_path
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from pydantic import ValidationError
from requests import HTTPError
from starlette.responses import RedirectResponse

logConfigFile = os.path.join(
    os.path.dirname(__file__), "..", "config", "logging.config"
)
logging.config.fileConfig(logConfigFile, disable_existing_loggers=False)
LOGGER = logging.getLogger("api.app.main")


apiPrefix = ""
description = """
Forest Access Management Admin Management API used by the Forest Access Management application
to define admin access to forest applications.
"""


def custom_generate_unique_id(route: APIRouter):
    # The outcome of this is on openapi spec's "operationId" field.
    # When api client is generated, this will be used for function/method name.
    return f"{route.name}"  # f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title="Forest Access Management - FAM - Admin Management API",
    description=description,
    version="0.0.1",
    contact={
        "name": "Team Heartwood",
        "url": "https://apps.nrs.gov.bc.ca/int/confluence/display/FSAST1/Team+Heartwood",
        "email": "SIBIFSAF@Victoria1.gov.bc.ca",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    root_path=get_root_path(),
    generate_unique_id_function=custom_generate_unique_id,
)

# Temporary assign openapi_version = "3.0.3" to fix not able to generate correct api-client for frontend.
# Due to current fastapi==0.100.0, this default to swagger spec version to 3.1.0, but version 3.1.0 is not
# yet well supported by openapi-generator.
# Also, FastAPI only 'hardcoded' with '3.0.3' it isn't truly convert to 3.0.3 openapi spec. However, it does
# temporarily solve openapi-generator issue.
app.openapi_version = "3.0.3"

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allow_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
app.add_exception_handler(HTTPError, requests_http_error_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)


app.include_router(
    router_smoke_test.router, prefix=apiPrefix + "/smoke_test", tags=["Smoke Test"]
)
app.include_router(
    router_application_admin.router,
    prefix=apiPrefix + "/application-admins",
    tags=["FAM Application Admin"],
)
app.include_router(
    router_access_control_privilege.router,
    prefix=apiPrefix + "/access-control-privileges",
    tags=["FAM Access Control Privileges"],
)
app.include_router(
    router_admin_user_accesses.router,
    prefix=apiPrefix + "/admin-user-accesses",
    tags=["Admin User Accesses"],
)


@app.get("/", include_in_schema=False, tags=["docs"])
def main():
    return RedirectResponse(url="/docs/")


handler = Mangum(app)
