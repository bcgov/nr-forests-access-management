from http import HTTPStatus

import pytest
from api.app.constants import (ERROR_CODE_UPSTREAM_CONNECTION_ERROR,
                               ERROR_CODE_UPSTREAM_TIMEOUT)
from requests.exceptions import ConnectionError, Timeout


@pytest.mark.parametrize(
    "exception_class, expected_failure_code, expected_message",
    [
        (
            Timeout,
            ERROR_CODE_UPSTREAM_TIMEOUT,
            "Upstream service timed out.",
        ),
        (
            ConnectionError,
            ERROR_CODE_UPSTREAM_CONNECTION_ERROR,
            "Could not connect to upstream service.",
        ),
    ],
)
def test_registered_gateway_timeout_handler_on_router(
    test_client_fixture_unit,
    exception_class,
    expected_failure_code,
    expected_message,
):
    """Ensure app-level exception registration handles raised upstream errors."""
    app = test_client_fixture_unit.app
    route_path = f"/__tests__/gateway-timeout/{exception_class.__name__}"

    async def raise_upstream_exception():
        raise exception_class("simulated upstream error")

    app.add_api_route(route_path, raise_upstream_exception, methods=["GET"])

    try:
        response = test_client_fixture_unit.get(route_path)
    finally:
        app.router.routes = [
            route for route in app.router.routes if getattr(route, "path", None) != route_path
        ]

    assert response.status_code == HTTPStatus.GATEWAY_TIMEOUT
    assert response.json() == {
        "failureCode": expected_failure_code,
        "message": expected_message,
    }
