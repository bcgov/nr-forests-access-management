import logging.config
import os.path

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from .routers import \
    router_application, \
    router_user_role_assignment
    # router_role, \
    # router_user, \


from mangum import Mangum

from .jwt_validation import init_jwks

from .config import get_root_path

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

origins = [
    "*",
    "http://127.0.0.1:5432"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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

# Removing these two routers because they are not in scope for MVP

# app.include_router(router_user.router,
#                    prefix=apiPrefix + '/fam_users',
#                    tags=["FAM Users"])
# app.include_router(router_role.router,
#                    prefix=apiPrefix + '/fam_roles',
#                    tags=["FAM Roles"])

# If we initialize this in main then it doesn't call Cognito on every api call
init_jwks()

handler = Mangum(app)
