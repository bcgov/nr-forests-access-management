import logging

import requests
from api.app.schemas import GCNotifyGrantAccessEmailParamSchema
from api.config import config

LOGGER = logging.getLogger(__name__)

GC_NOTIFY_EMAIL_BASE_URL = "https://api.notification.canada.ca"
GC_NOTIFY_GRANT_ACCESS_EMAIL_TEMPLATE_ID = "0806a36e-b33d-4e43-a401-b1eb92777116"


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

    def send_user_access_granted_email(
        self, params: GCNotifyGrantAccessEmailParamSchema
    ):
        """
        Send grant access email
        """
        # GC Notify does not have sufficient conditional rendering, cannot send None to variable, and does not support
        # 'variable' within coditional text. Easier to do this in code.
        application_role_granted_text = __to_application_role_granted_text(params)
        organization_list_text = __to_organization_list_text(params)
        contact_message = __to_contact_message(params)
        personalisation_params = {
            "first_name": params.first_name,
            "last_name": params.last_name,
            "application_role_granted_text": application_role_granted_text,
            "organization_list_text": organization_list_text,
            "contact_message": contact_message
        }

        email_params = {
            "email_address": params.send_to_email,
            "template_id": self.grant_access_email_template_id,
            "personalisation": personalisation_params,
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


def __to_contact_message(params: GCNotifyGrantAccessEmailParamSchema):
    # GC Notify does not have sufficient conditional rendering, cannot send None to variable, and does not support
    # 'variable' within coditional text. Easier to do this in code.
    return (
        f"Please contact your administrator {params.application_team_contact_email} if you have any issues accessing the application."
        if params.application_team_contact_email is not None
        else "Please contact your administrator if you have any issues accessing the application."
    )

def __to_application_role_granted_text(params: GCNotifyGrantAccessEmailParamSchema):
    granted_app_role_no_org_txt = f"You have been granted access to **{params.application_description}** with a **{params.role_display_name}** role."
    granted_app_role_with_org_txt = f"You have been granted access to **{params.application_description}** with a **{params.role_display_name}** role for the following organizations:"
    return granted_app_role_no_org_txt if params.organization_list is None else granted_app_role_with_org_txt

def __to_organization_list_text(params: GCNotifyGrantAccessEmailParamSchema):
    org_list = params.organization_list
    # format to: "* bold[client_name] (Client number: 111)[new line]* bold(client_name) (Client number: 222)"
    org_formatted_list_str = "\n".join([f"* **{item.client_name}** (Client number: {item.forest_client_number})" for item in org_list])
    return org_formatted_list_str