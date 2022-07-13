import logging.config
import os.path
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from .routers import fam_router

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

tags_metadata = [{
        "name": "Forest Access Management - FAM",
        "description": "Controls the user access to different Forest based" +
                       "applications and what roles different users will have " +
                       "once logged in"
    },
]

description = """
Forest Access Management API used by the Forest Access Management application to
Define who has access to what apps, and what roles they will operate under once
access is granted.
"""

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
    openapi_tags=tags_metadata
)

origins = [
    "http://127.0.0.1:5432"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.get("/")
def main():
    return RedirectResponse(url="/docs/")


app.include_router(fam_router.router, prefix='/api/v1')


if __name__  == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
