import json
from urllib.request import urlopen
import logging

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

rsa_key = {}
for key in jwks["keys"]:
    if key["kid"] == "bcscencryption":
        rsa_key = {
            "kty": key["kty"],
            "kid": key["kid"],
            "use": key["use"],
            "n": key["n"],
            "e": key["e"],
        }
    break

LOGGER.warning(rsa_key)

