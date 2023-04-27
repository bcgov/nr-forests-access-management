import json
from urllib.request import urlopen
import logging
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from base64 import b64decode, b64encode

LOGGER = logging.getLogger(__name__)

try:
    jwks = None

    url = "https://qz39ajtria.execute-api.ca-central-1.amazonaws.com/v1/bcsc/jwks.json"
    with urlopen(url) as response:
        jwks = json.loads(response.read().decode("utf-8"))

except Exception as e:
    LOGGER.error(f"init_jwks function failed to reach AWS: {e}.")
    LOGGER.error("Backend API will not work properly.")
    raise e

jwk = {}
for key in jwks["keys"]:
    if key["kid"] == "bcscencryption":
        jwk = {
            "kty": key["kty"],
            "kid": key["kid"],
            "use": key["use"],
            "n": key["n"],
            "e": key["e"],
        }
    break

LOGGER.warning(jwk)

pubkey = jwk["n"]

msg = "1000 Monkeys"
keyDER = b64decode(pubkey)
keyPub = RSA.importKey(keyDER)
cipher = PKCS1_OAEP.new(keyPub)
cipher_text = cipher.encrypt(msg.encode())
emsg = b64encode(cipher_text)

LOGGER.warning(emsg)

test_url = (
    "https://qz39ajtria.execute-api.ca-central-1.amazonaws.com/v1/bcsc/encryption_test"
)

raw_response = None

with urlopen(test_url, data=emsg) as response:
    raw_response = response.read().decode("utf-8")

LOGGER.warning(raw_response)
