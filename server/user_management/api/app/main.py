import logging.config
import os.path

from fastapi import APIRouter, FastAPI
from starlette.responses import RedirectResponse

from api.config.config import get_root_path
from .routers import router_smoke_test

logConfigFile = os.path.join(
    os.path.dirname(__file__), "..", "config", "logging.config"
)

logging.config.fileConfig(logConfigFile, disable_existing_loggers=False)

LOGGER = logging.getLogger("api.app.main")


apiPrefix = ""
description = """
Forest Access Management API used by the Forest Access Management application
to define admin access to forest applications.
"""


def custom_generate_unique_id(route: APIRouter):
    # The outcome of this is on openapi spec's "operationId" field.
    # When api client is generated, this will be used for function/method name.
    return f"{route.name}"  # f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title="Forest Access Management - FAM - User Management API",
    description=description,
    version="0.0.1",
    contact={
        "name": "Guy Lafleur",
        "url": "https://en.wikipedia.org/wiki/Guy_Lafleur",
        "email": "guy.lafleur@montreal.canadians.ca",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    root_path=get_root_path(),
    generate_unique_id_function=custom_generate_unique_id,
)

app.include_router(
    router_smoke_test.router, prefix=apiPrefix + "/smoke_test", tags=["Smoke Test"]
)


@app.get("/", include_in_schema=False, tags=["docs"])
def main():
    return RedirectResponse(url="/docs/")
