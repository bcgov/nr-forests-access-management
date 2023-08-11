import logging

from api.app.integration.gc_notify import GCNotifyEmailService
from api.app.schemas import GCNotifyEmailParam
from fastapi import APIRouter

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.post("/send", response_model=str)
def send_email(email_params: GCNotifyEmailParam):
    gc_notify_api = GCNotifyEmailService()
    result = gc_notify_api.send_email(email_params)

    return result["id"]
