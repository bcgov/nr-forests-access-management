import logging.config
import os.path

from pydantic import ValidationError

from api.app.exception_handlers import (
    requests_http_error_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from api.config.config import get_allow_origins, get_root_path, is_bcsc_key_enabled
from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from requests import HTTPError
from starlette.responses import RedirectResponse

from .jwt_validation import init_jwks
from .kms_lookup import init_bcsc_public_key
from .routers import (
    router_application,
    router_bcsc_proxy,
    router_forest_client,
    router_idim_proxy,
    router_smoke_test,
    router_user_role_assignment,
    router_user_terms_conditions,
    router_guards,
    router_user,
    router_permission_audit
)

logConfigFile = os.path.join(
    os.path.dirname(__file__), "..", "config", "logging.config"
)

logging.config.fileConfig(logConfigFile, disable_existing_loggers=False)

LOGGER = logging.getLogger("api.app.main")

tags_metadata = [
    {
        "name": "Forest Access Management - FAM",
        "description": "Controls the user access to different Forest based"
        + "applications and what roles different users will "
        + "have once logged in",
    },
]

description = """
Forest Access Management API used by the Forest Access Management application
to Define who has access to what apps, and what roles they will operate under
 once access is granted.
"""


def custom_generate_unique_id(route: APIRouter):
    # The outcome of this is on openapi spec's "operationId" field.
    # When api client is generated, this will be used for function/method name.
    return f"{route.name}"  # f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title="Forest Access Management - FAM - API",
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
    openapi_tags=tags_metadata,
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


@app.get("/", include_in_schema=False, tags=["docs"])
def main():
    return RedirectResponse(url="/docs/")


apiPrefix = ""
app.include_router(
    router_application.router,
    prefix=apiPrefix + "/fam_applications",
    tags=["FAM Applications"],
)
app.include_router(
    router_user_role_assignment.router,
    prefix=apiPrefix + "/user_role_assignment",
    tags=["FAM User Role Assignment"],
)
app.include_router(
    router_forest_client.router,
    prefix=apiPrefix + "/forest_clients",
    dependencies=[Depends(router_guards.authorize)],
    tags=["FAM Forest Clients"],
)
app.include_router(
    router_idim_proxy.router,
    prefix=apiPrefix + "/identity_search",
    dependencies=[Depends(router_guards.authorize)],
    tags=["IDIR/BCeID Proxy"],
)
app.include_router(
    router_user_terms_conditions.router,
    prefix=apiPrefix + "/user_terms_conditions",
    dependencies=[Depends(router_guards.authorize)],
    tags=["FAM User Terms and Conditions"],
)
app.include_router(
    router_user.router,
    prefix=apiPrefix + "/users",
    dependencies=[Depends(router_guards.verify_api_key_for_update_user_info)],
    tags=["FAM User"],
)
app.include_router(
    router_permission_audit.router,
    prefix=apiPrefix + "/permission-audit-history",
    dependencies=[Depends(router_guards.authorize)],
    tags=["Permission Audit"],
)



# This router is used to proxy the BCSC userinfo endpoint

app.include_router(
    router_bcsc_proxy.router, prefix=apiPrefix + "/bcsc", tags=["BCSC Proxy"]
)

app.include_router(
    router_smoke_test.router, prefix=apiPrefix + "/smoke_test", tags=["Smoke Test"]
)

# If we initialize this in main then it doesn't call Cognito on every api call
init_jwks()

# If we initialize the key lookup then it doesn't call KMS on every api call

if is_bcsc_key_enabled():
    LOGGER.info("BCSC Key endpoint enabled")
    init_bcsc_public_key()
else:
    LOGGER.info("BCSC Key endpoint disabled")

handler = Mangum(app)
