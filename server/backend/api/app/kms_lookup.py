import logging
import boto3

from api.config.config import get_aws_region, get_bcsc_key_id

_bcsc_public_key = None
_kms_client = None

LOGGER = logging.getLogger(__name__)


def init_bcsc_public_key():
    global _bcsc_public_key
    global _kms_client

    region_name = get_aws_region()
    session = boto3.session.Session()
    _kms_client = session.client(service_name="kms", region_name=region_name)

    key_id = get_bcsc_key_id()
    LOGGER.debug(f"Looking up kms key for bcsc with key of {key_id}...")
    try:
        _bcsc_public_key = _kms_client.get_public_key(KeyId=key_id)
        LOGGER.info(f"Retrieved public key: {_bcsc_public_key}")

    except Exception as e:
        LOGGER.error(f"init_kms function failed to reach AWS: {e}.")
        LOGGER.error("BCSC userinfo endpoint will not work properly.")
        raise e


def decrypt(encrypted_token):

    response = _kms_client.decrypt(
        CiphertextBlob=encrypted_token,
        KeyId=get_bcsc_key_id(),
        EncryptionAlgorithm="RSAES_OAEP_SHA_256",
    )

    return response["Plaintext"]


def encrypt(msg):

    response = _kms_client.encrypt(
        KeyId=get_bcsc_key_id(), Plaintext=msg, EncryptionAlgorithm="RSAES_OAEP_SHA_256"
    )

    return response["CiphertextBlob"]
