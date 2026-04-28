import json
from http import HTTPStatus

import pytest
from api.app.constants import (ERROR_CODE_UPSTREAM_CONNECTION_ERROR,
                               ERROR_CODE_UPSTREAM_TIMEOUT)
from api.app.exception_handlers import requests_gateway_timeout_error_handler
from requests import Request as RequestsRequest
from requests.exceptions import ConnectionError, Timeout
from starlette.requests import Request


@pytest.mark.parametrize(
    "exception_factory, expected_failure_code, expected_message",
    [
        (
            lambda: Timeout("upstream timeout"),
            ERROR_CODE_UPSTREAM_TIMEOUT,
            "Upstream service timed out.",
        ),
        (
            lambda: ConnectionError("upstream connection error"),
            ERROR_CODE_UPSTREAM_CONNECTION_ERROR,
            "Could not connect to upstream service.",
        ),
    ],
)
def test_requests_gateway_timeout_error_handler_returns_gateway_timeout(
    exception_factory,
    expected_failure_code,
    expected_message,
):
    """Ensure timeout/connectivity failures are mapped to a 504 response."""
    request = Request(
        {
            "type": "http",
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": "/test-endpoint",
            "query_string": b"application_id=1",
            "headers": [],
            "client": ("127.0.0.1", 5000),
            "server": ("testserver", 80),
            "root_path": "",
        }
    )

    exception = exception_factory()
    exception.request = RequestsRequest(
        "GET", "https://example-upstream.test/path"
    ).prepare()

    response = requests_gateway_timeout_error_handler(request, exception)

    assert response.status_code == HTTPStatus.GATEWAY_TIMEOUT
    assert json.loads(response.body) == {
        "failureCode": expected_failure_code,
        "message": expected_message,
    }
