import logging

import requests
from api.app.schemas import GCNotifyGrantDelegatedAdminEmailParam
from api.config import config

LOGGER = logging.getLogger(__name__)

GC_NOTIFY_EMAIL_BASE_URL = "https://api.notification.canada.ca"
GC_NOTIFY_GRANT_DELEGATED_ADMIN_EMAIL_TEMPLATE_ID = "9abff613-e507-4562-aae0-008317dfe3b9"
# Template id for granting application admin, we will use this later
GC_NOTIFY_GRANT_APP_ADMIN_EMAIL_TEMPLATE_ID = "230bca59-4906-40b2-8f2b-2f6186a98663"


class GCNotifyEmailService:
    """
    The class is used for sending email
    """

    TIMEOUT = (5, 10)  # Timeout (connect, read) in seconds.

    def __init__(self):
        self.API_KEY = config.get_gc_notify_email_api_key()
        self.email_base_url = GC_NOTIFY_EMAIL_BASE_URL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "ApiKey-v1 " + self.API_KEY,
        }

        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def send_delegated_admin_granted_email(self, params: GCNotifyGrantDelegatedAdminEmailParam):
        """
        Send email notification for new delegated admin
        """
        # GC Notify does not have sufficient conditional rendering, cannot send None to variable, and does not support
        # 'variable' within coditional text. Easier to do this in code.
        contact_message = (
            f"Please contact your administrator {params.application_team_contact_email} if you have any questions."
            if params.application_team_contact_email is not None
            else "Please contact your administrator if you have any questions."
        )

        email_params = {
            "email_address": params.send_to_email_address,
            "template_id": GC_NOTIFY_GRANT_DELEGATED_ADMIN_EMAIL_TEMPLATE_ID,
            "personalisation": {
                **params.__dict__,
                "contact_message": contact_message
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