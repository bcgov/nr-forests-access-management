import logging

import requests
from api.app.schemas import GCNotifyGrantAccessEmailParam
from api.config import config

LOGGER = logging.getLogger(__name__)

GC_NOTIFY_EMAIL_BASE_URL = "https://api.notification.canada.ca"
GC_NOTIFY_GRANT_ACCESS_EMAIL_TEMPLATE_ID = "cd46fd74-7d79-4576-97ef-8b93297def24"


class GCNotifyEmailService:
    """
    The class is used for sending email
    """

    TIMEOUT = (5, 10)  # Timeout (connect, read) in seconds.

    def __init__(self):
        # For lower environment to send email, FAM uses GC Notify 'team and safelist' API_KEY type.
        # For production it uses 'live' key.
        # ref: https://documentation.notification.canada.ca/en/keys.html
        self.API_KEY = config.get_gc_notify_email_api_key()
        self.grant_access_email_template_id = GC_NOTIFY_GRANT_ACCESS_EMAIL_TEMPLATE_ID
        self.email_base_url = GC_NOTIFY_EMAIL_BASE_URL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "ApiKey-v1 " + self.API_KEY,
        }

        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def send_user_access_granted_email(self, params: GCNotifyGrantAccessEmailParam):
        """
        Send grant access email
        """
        # GC Notify does not have sufficient conditional rendering, cannot send None to variable, and does not support
        # 'variable' within coditional text. Easier to do this in code.
        contact_message = (
            f"Please contact your administrator {params.application_team_contact_email} if you have any issues accessing the application."
            if params.application_team_contact_email is not None
            else "Please contact your administrator if you have any issues accessing the application."
        )

        email_params = {
            "email_address": params.send_to_email,
            "template_id": self.grant_access_email_template_id,
            "personalisation": {
                **params.__dict__,
                "contact_message": contact_message
            },
        }
        LOGGER.debug(f"Sending user access granted email with param {email_params}")
        gc_notify_email_send_url = f"{self.email_base_url}/v2/notifications/email"

        r = self.session.post(
            gc_notify_email_send_url, timeout=self.TIMEOUT, json=email_params
        )
        r.raise_for_status()  # There is a general error handler, see: requests_http_error_handler
        send_email_result = r.json()

        LOGGER.debug(f"Send Email result: {send_email_result}")
        return send_email_result
