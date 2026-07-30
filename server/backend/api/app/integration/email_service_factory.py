import logging

from api.app.constants import EmailProvider
from api.app.integration.ches import ChesEmailService
from api.app.integration.gc_notify import GCNotifyEmailService
from api.config import config

LOGGER = logging.getLogger(__name__)


def get_email_service():
    """
    Return the email integration selected by the EMAIL_PROVIDER env var.

    Defaults to GC Notify so deploying does not change behaviour until an
    environment is explicitly flipped to CHES. Both providers expose the same
    send_* methods and accept the same param schema, so callers are unaffected by
    the choice.

    When GC Notify is retired, drop the branch and return ChesEmailService()
    unconditionally (the factory seam can stay).
    """
    if config.get_email_provider() == EmailProvider.CHES.value:
        return ChesEmailService()
    return GCNotifyEmailService()
