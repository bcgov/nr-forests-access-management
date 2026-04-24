import json
import logging
import sys
from http import HTTPStatus

from api.app.constants import (ERROR_CODE_UPSTREAM_CONNECTION_ERROR,
                               ERROR_CODE_UPSTREAM_TIMEOUT)
from fastapi import Request
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import ValidationError
from requests import HTTPError
from requests.exceptions import ConnectionError, RequestException, Timeout

LOGGER = logging.getLogger(__name__)


async def requests_gateway_timeout_error_handler(
    request: Request, exc: RequestException
):
    """
    Handle outbound requests timeout/connectivity errors and return
    gateway timeout.

    This handler is intended for requests.exceptions.Timeout and
    requests.exceptions.ConnectionError raised from integration calls to
    upstream services.
    """
    host = getattr(getattr(request, "client", None), "host", None)
    port = getattr(getattr(request, "client", None), "port", None)
    url = (
        f"{request.url.path}?{request.query_params}"
        if request.query_params
        else request.url.path
    )
    upstream_url = getattr(getattr(exc, "request", None), "url", None)

    if isinstance(exc, Timeout):
        error_content = {
            "failureCode": ERROR_CODE_UPSTREAM_TIMEOUT,
            "message": "Upstream service timed out.",
        }
    elif isinstance(exc, ConnectionError):
        error_content = {
            "failureCode": ERROR_CODE_UPSTREAM_CONNECTION_ERROR,
            "message": "Could not connect to upstream service.",
        }
    else:
        error_content = {
            "failureCode": ERROR_CODE_UPSTREAM_TIMEOUT,
            "message": "Upstream service timed out.",
        }

    LOGGER.error(
        f'{host}:{port} - "{request.method} {url}" '
        f"{HTTPStatus.GATEWAY_TIMEOUT} Gateway Timeout "
        f"upstream={upstream_url} <{exc}>"
    )

    return JSONResponse(
        status_code=HTTPStatus.GATEWAY_TIMEOUT,
        content=error_content,
    )


async def requests_http_error_handler(request: Request, exc: HTTPError):
    """
    When using Python 'requests' package (mostly for server integration with external to issue http request),
    it raises requests.exceptions.HTTPError for 4xx.
    However, FastAPI sees this as Exception other than its' own HTTPException and will instead return 500 error.
    So we handle this HTTPError as a custom error handler specifically here.

    scope:
    * This handler is registered for requests.HTTPError only, typically raised from outbound requests calls (such as GC Notify, IDIM Proxy API call).
    * FastAPI and generic Python exceptions, or Pydantic validation errors are not handled by this handler.
    * It tries to parse response text as JSON from different error payload shapes
      returned from upstream services:
      - failureCode/message style
      - errors[0].error / errors[0].message style
      - non-JSON or unknown shape fallback to raw text or HTTP reason
    """
    status_code = exc.response.status_code
    host = getattr(getattr(request, "client", None), "host", None)
    port = getattr(getattr(request, "client", None), "port", None)
    url = (
        f"{request.url.path}?{request.query_params}"
        if request.query_params
        else request.url.path
    )
    raw_response_text = exc.response.text

    try:
        response_text = json.loads(raw_response_text) if raw_response_text else {}
    except json.JSONDecodeError:
        response_text = {}

    failure_code = None
    if isinstance(response_text, dict) and "failureCode" in response_text:
        failure_code = response_text["failureCode"]
    elif (
        isinstance(response_text, dict)
        and "errors" in response_text
        and "error" in response_text["errors"][0]
    ):
        # this is the error format for gc notify
        failure_code = response_text["errors"][0]["error"]

    error_message = None
    if isinstance(response_text, dict) and "message" in response_text:
        error_message = response_text["message"]
    elif (
        isinstance(response_text, dict)
        and "errors" in response_text
        and "message" in response_text["errors"][0]
    ):
        # this is the error format for gc notify
        error_message = response_text["errors"][0]["message"]
    else:
        error_message = raw_response_text or exc.response.reason

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
    exception_type, exception_value, _rest = sys.exc_info()
    exception_name = getattr(exception_type, "__name__", None)
    LOGGER.error(
        f'{host}:{port} - "{request.method} {url}" 500 Internal Server Error <{exception_name}: {exception_value}>'
    )
    return PlainTextResponse(str(exc), status_code=500)


async def validation_exception_handler(request: Request, exc: ValidationError):
    """
    Handles pydantic.ValidationError raised manually in service/validation code
    (e.g., from @model_validator or manual model instantiation).

    This is distinct from FastAPI's built-in RequestValidationError handler, which
    covers request body/query param parsing failures automatically.

    Returns the same {"detail": [...]} JSON shape as FastAPI's default 422 handler
    so frontend/client error handling only needs to deal with one format.
    The raw `input` and pydantic docs `url` fields are intentionally omitted
    to avoid leaking raw request data and internal details in responses.
    """
    LOGGER.error(
        f"Pydantic ValidationError occurred, cannot process request "
        f"{request.method} {request.url} with error {exc}"
    )
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content={
            "detail": [
                {
                    "loc": list(err["loc"]),
                    "msg": err["msg"],
                    "type": err["type"],
                }
                for err in exc.errors()
            ]
        },
    )