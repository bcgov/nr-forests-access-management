import logging

import requests
from api.app.schemas.schemas import GCNotifyGrantDelegatedAdminEmailParam
from api.app.utils.utils import is_success_response
from api.config import config

from .integration_data import tc_file_attach_base64

LOGGER = logging.getLogger(__name__)

GC_NOTIFY_EMAIL_BASE_URL = "https://api.notification.canada.ca"
GC_NOTIFY_GRANT_DELEGATED_ADMIN_EMAIL_TEMPLATE_ID = "4f36da24-7507-4813-8285-d66a254c1f88"
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
        application_role_granted_text = self.__to_application_role_granted_text(params)
        organization_list_text = self.__to_organization_list_text(params)
        contact_message = self.__to_contact_message(params)
        terms_conditions_comply_text = self.__to_terms_conditions_comply_text()

        personalisation_params = {
            "user_name": params.user_name,
            "first_name": params.first_name,
            "last_name": params.last_name,
            "application_name": params.application_description,
            "application_role_granted_text": application_role_granted_text,
            "organization_list_text": organization_list_text,
            "contact_message": contact_message,
            "terms_conditions_comply_text": ""  # empty will not be displayed by default, only BCEID user needs this.
        }

        if params.is_bceid_user == "yes":
            """
            Note:
                * About Terms and Conditions used in coding:
                    Ther current version of T&C file is : "2024-06-04-.FAM.terms.of.use.approved.by.WK.BB.pdf".
                    A copy is deposited under frontend's /public folder so it can be public accessible with a
                    url friendly file name "2024-06-04-fam-terms-conditions.pdf".
                    Contact Olga or Kajol for the latest copy.
                    If there is version update, developers need to be aware the changes needs to be on both
                    frontend and the backend (frontend has a component with word-by-word coded for T&C)
            """
            # only include file as GC Notify attachment for T&C.
            personalisation_params |= {
                "terms_conditions_comply_text": terms_conditions_comply_text,
            }

        email_params = {
            "email_address": params.send_to_email_address,
            "template_id": GC_NOTIFY_GRANT_DELEGATED_ADMIN_EMAIL_TEMPLATE_ID,
            "personalisation": personalisation_params
        }
        gc_notify_email_send_url = f"{self.email_base_url}/v2/notifications/email"

        r = self.session.post(
            gc_notify_email_send_url, timeout=self.TIMEOUT, json=email_params
        )

        if not is_success_response(r):
            # Add a debug for python response object for easy debugging purpose. After raising python
            # exception (raise_for_status()), the error message is not printed from the caller.
            LOGGER.debug(f"Email sending error response: {r.__dict__}")
            r.raise_for_status()

        send_email_result = r.json()

        LOGGER.debug(f"Send Email result: {send_email_result}")
        return send_email_result

    def __to_contact_message(self, params: GCNotifyGrantDelegatedAdminEmailParam):
        return (
            f"Please contact your administrator {params.application_team_contact_email} if you have any questions."
            if params.application_team_contact_email is not None
            else "If you have any questions, please contact your administrator."
        )

    def __to_application_role_granted_text(self, params: GCNotifyGrantDelegatedAdminEmailParam):
        granted_app_role_no_org_txt = f"Grant **{params.role_display_name}** role to users."
        granted_app_role_with_org_txt = f"Grant **{params.role_display_name}** role to users in:"
        return granted_app_role_no_org_txt if params.organization_list is None else granted_app_role_with_org_txt

    def __to_organization_list_text(self, params: GCNotifyGrantDelegatedAdminEmailParam):
        org_list = params.organization_list
        if (org_list is None):
            return ""

        # below is formatted to: "* bold[client_name] (Client number: 111)[new line]* bold(client_name) (Forest Client: 222)"
        org_formatted_list_str = "\n".join([f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&#x0095; **{item.client_name}** (Forest Client: {item.forest_client_number})" for item in org_list])
        return org_formatted_list_str

    def __to_terms_conditions_comply_text(self):
            frontend_url = config.get_env_var("ALLOW_ORIGIN") if config.is_on_aws() else "https://fam-dev.nrs.gov.bc.ca"  # default to dev.
            tc_filename = "2024-06-04-fam-terms-conditions.pdf"
            txt = f"As a Delegated Administrator, you must comply with our [terms and conditions]({frontend_url}/{tc_filename})."
            return txt
