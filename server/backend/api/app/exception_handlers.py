import json
import logging
import sys
from http import HTTPStatus

from fastapi import Request
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import ValidationError
from requests import HTTPError

LOGGER = logging.getLogger(__name__)


async def requests_http_error_handler(request: Request, exc: HTTPError):
    """
    When using Python 'requests' package (mostly for server integration with external to issue http request),
    it raises requests.exceptions.HTTPError for 4xx.
    However, FastAPI sees this as Exception other than its' own HTTPException and will instead return 500 error.
    So we handle this HTTPError as a custom error handler specifically here.
    """
    status_code = exc.response.status_code
    host = getattr(getattr(request, "client", None), "host", None)
    port = getattr(getattr(request, "client", None), "port", None)
    url = (
        f"{request.url.path}?{request.query_params}"
        if request.query_params
        else request.url.path
    )
    response_text = json.loads(exc.response.text)

    failure_code = None
    if "failureCode" in response_text:
        failure_code = response_text["failureCode"]
    elif "errors" in response_text and "error" in response_text["errors"][0]:
        # this is the error format for gc notify
        failure_code = response_text["errors"][0]["error"]

    error_message = None
    if "message" in response_text:
        error_message = response_text["message"]
    elif "errors" in response_text and "message" in response_text["errors"][0]:
        # this is the error format for gc notify
        error_message = response_text["errors"][0]["message"]

    error_content = {
        "failureCode": failure_code,
        "message": error_message,
    }

    LOGGER.error(
        f'{host}:{port} - "{request.method} {url}" {status_code} {exc.response.reason}, '
        f"error content - {error_content}"
    )
    # For HTTPError's 401/403 specifically - return 500 Internal Server Error.
    # (so FAM frontend does not misinterprete 401/403 as authentication/authorization problem from user request)
    if status_code == HTTPStatus.UNAUTHORIZED or status_code == HTTPStatus.FORBIDDEN:
        return JSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, content=error_content
        )

    return JSONResponse(status_code=exc.response.status_code, content=error_content)


async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> PlainTextResponse:
    """
    This middleware will log all unhandled exceptions.
    Unhandled exceptions are all exceptions that are not HTTPExceptions or RequestValidationErrors.
    """
    LOGGER.debug("Custom unhandled_exception_handler was called")
    host = getattr(getattr(request, "client", None), "host", None)
    port = getattr(getattr(request, "client", None), "port", None)
    url = (
        f"{request.url.path}?{request.query_params}"
        if request.query_params
        else request.url.path
    )
    exception_type, exception_value, *rest = sys.exc_info()
    exception_name = getattr(exception_type, "__name__", None)
    LOGGER.error(
        f'{host}:{port} - "{request.method} {url}" 500 Internal Server Error <{exception_name}: {exception_value}>'
    )
    return PlainTextResponse(str(exc), status_code=500)


async def validation_exception_handler(request: Request, exc: ValidationError):
    LOGGER.error(
        f'Pydantic ValidationError occurred, cannot process request {request} with error {exc}'
    )
    return PlainTextResponse(str(exc), status_code=HTTPStatus.UNPROCESSABLE_ENTITY)