import logging
import pytest
from requests import HTTPError
from api.app.integration.gc_notify import GCNotifyEmailService
from api.app.schemas import GCNotifyEmailParam

LOGGER = logging.getLogger(__name__)


class TestGCNotifyEmailServiceClass(object):
    """
    Testing GCNotiryEmailService class with real remote API calls.
    Will ignore the successful case, as we don't want to send the real email.
    """

    gc_notify_email_service: GCNotifyEmailService

    def setup_class(self):
        self.gc_notify_email_service = GCNotifyEmailService()

    def test_verify_init(self):
        # Quick Verifying for init not empty
        assert self.gc_notify_email_service.email_template_id is not None
        assert self.gc_notify_email_service.email_base_url is not None
        assert self.gc_notify_email_service.API_KEY is not None
        assert (
            self.gc_notify_email_service.headers["Authorization"]
            == "ApiKey-v1 " + self.gc_notify_email_service.API_KEY
        )

    def test_with_invalid_email_address(self):
        """
        The test checks the error handling when provide an invalid email address
        """
        test_params: GCNotifyEmailParam = GCNotifyEmailParam(
            **{
                "user_name": "cmeng",
                "application_name": "fam",
                "send_to_email": "catherine.meng",
            }
        )

        with pytest.raises(Exception) as excinfo:
            self.gc_notify_email_service.send_granted_access_email(test_params)

        assert excinfo.type == HTTPError
        assert excinfo.match("400 Client Error: Bad Request")
