import logging.config
import os.path

from api.app import jwt_validation
from api.config.config import get_allow_origins, get_root_path, is_bcsc_key_enabled
from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from mangum import Mangum

from .jwt_validation import init_jwks
from .routers import (router_application, router_forest_client, router_role,
                      router_user, router_user_role_assignment,
                      router_bcsc_proxy)
from .kms_lookup import init_bcsc_public_key


logConfigFile = os.path.join(
    os.path.dirname(__file__),
    '..',
    'config',
    'logging.config')

logging.config.fileConfig(
    logConfigFile,
    disable_existing_loggers=False
)

LOGGER = logging.getLogger('api.app.main')

tags_metadata = [
    {
        "name": "Forest Access Management - FAM",
        "description": "Controls the user access to different Forest based" +
                       "applications and what roles different users will " +
                       "have once logged in"
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
    version='0.0.1',
    contact={
        "name": "Guy Lafleur",
        "url": "https://en.wikipedia.org/wiki/Guy_Lafleur",
        "email": "guy.lafleur@montreal.canadians.ca",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_tags=tags_metadata,
    root_path=get_root_path(),
    generate_unique_id_function=custom_generate_unique_id
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allow_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.get("/", include_in_schema=False, tags=["docs"])
def main():
    return RedirectResponse(url="/docs/")


apiPrefix = ''
app.include_router(router_application.router,
                   prefix=apiPrefix + '/fam_applications',
                   tags=["FAM Applications"])
app.include_router(router_user_role_assignment.router,
                   prefix=apiPrefix + '/user_role_assignment',
                   tags=["FAM User Role Assignment"])
app.include_router(router_forest_client.router,
                   prefix=apiPrefix + '/forest_clients',
                   dependencies=[Depends(jwt_validation.authorize)],
                   tags=["FAM Forest Clients"])

# These two routers are disabled for MVP

app.include_router(router_user.router,
                   prefix=apiPrefix + '/fam_users',
                   tags=["FAM Users"])
app.include_router(router_role.router,
                   prefix=apiPrefix + '/fam_roles',
                   tags=["FAM Roles"])

# This router is used to proxy the BCSC userinfo endpoint

app.include_router(router_bcsc_proxy.router,
                   prefix=apiPrefix + '/bcsc',
                   tags=["BCSC Proxy"])

# If we initialize this in main then it doesn't call Cognito on every api call
init_jwks()

# If we initialize the key lookup then it doesn't call KMS on every api call

if is_bcsc_key_enabled():
    LOGGER.info("BCSC Key endpoint enabled")
    init_bcsc_public_key()
else:
    LOGGER.info("BCSC Key endpoint disabled")

handler = Mangum(app)
