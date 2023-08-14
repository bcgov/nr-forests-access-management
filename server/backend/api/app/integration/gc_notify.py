import logging

import requests
from api.app.schemas import GCNotifyEmailParam
from api.config import config

LOGGER = logging.getLogger(__name__)

GC_NOTIFY_EMAIL_BASE_URL = "https://api.notification.canada.ca"
GC_NOTIFY_EMAIL_TEMPLATE_ID = "cd46fd74-7d79-4576-97ef-8b93297def24"


class GCNotifyEmailService:
    """
    The class is used for sending email
    """

    TIMEOUT = (5, 10)  # Timeout (connect, read) in seconds.

    def __init__(self):
        self.API_KEY = config.get_gc_notify_email_api_key()
        self.email_template_id = GC_NOTIFY_EMAIL_TEMPLATE_ID
        self.email_base_url = GC_NOTIFY_EMAIL_BASE_URL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "ApiKey-v1 " + self.API_KEY,
        }

        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def send_granted_access_email(self, params: GCNotifyEmailParam):
        """
        Send grant access email
        """
        email_params = {
            "email_address": params.send_to_email,
            "template_id": self.email_template_id,
            "personalisation": {
                "username": params.user_name,
                "appname": params.application_name,
            },
        }
        gc_notify_email_send_url = f"{self.email_base_url}/v2/notifications/email"

        r = self.session.post(
            gc_notify_email_send_url, timeout=self.TIMEOUT, json=email_params
        )
        r.raise_for_status()  # There is a general error handler, see: requests_http_error_handler
        send_email_result = r.json()

        LOGGER.debug(f"Send Email result: {send_email_result}")
        return send_email_result
