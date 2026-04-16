import functools
import logging
import time

from api.app.schemas.fam_application import FamApplicationSchema
from api.app.schemas.requester import RequesterSchema

LOGGER = logging.getLogger(__name__)


def endpoint_timing_dec(endpoint_name: str):
    """
    Decorator that logs endpoint execution time from start to finish.

    This is intended for router handlers where `requester` and `application`
    are available as keyword arguments from dependency injection.
    """

    def decorator(original_func):
        @functools.wraps(original_func)
        def decorated_func(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                return original_func(*args, **kwargs)
            finally:
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                requester: RequesterSchema | None = kwargs.get("requester")
                application: FamApplicationSchema | None = kwargs.get("application")

                LOGGER.info(
                    "Endpoint timing - %s completed in %.2f ms. requester=%s, app=%s(%s)",
                    endpoint_name,
                    elapsed_ms,
                    getattr(requester, "user_name", None),
                    getattr(application, "application_name", None),
                    getattr(application, "application_id", None),
                )

        return decorated_func

    return decorator
