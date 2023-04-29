import logging
from fastapi import APIRouter, Request, Response, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import requests
from jose import jwt
from fastapi import HTTPException
from .. import kms_lookup
from api.config import config
from base64 import b64decode, b64encode

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.get("/dev/userinfo", status_code=200)
def bcsc_userinfo_dev(request: Request):
    return bcsc_userinfo(request, "https://idtest.gov.bc.ca/oauth2/userinfo")


@router.get("/test/userinfo", status_code=200)
def bcsc_userinfo_test(request: Request):
    return bcsc_userinfo(request, "https://idtest.gov.bc.ca/oauth2/userinfo")


@router.get("/prod/userinfo", status_code=200)
def bcsc_userinfo_prod(request: Request):
    return bcsc_userinfo(request, "https://id.gov.bc.ca/oauth2/userinfo")


def bcsc_userinfo(request: Request, bcsc_userinfo_uri):

    """
    Proxy the BCSC userinfo endpoint and decode the result
    """

    raw_response = requests.get(url=bcsc_userinfo_uri, headers=request.headers).text

    decrypted_token = raw_response

    if config.is_bcsc_key_enabled():
        decrypted_token = kms_lookup.decrypt(raw_response)

    decoded_payload = jwt.decode(
        decrypted_token, None, options={"verify_signature": False, "verify_aud": False}
    )

    aud = decoded_payload["aud"]
    valid_auds = [
        "ca.bc.gov.flnr.fam.dev",
        "ca.bc.gov.flnr.fam.test",
        "ca.bc.gov.flnr.fam",
    ]
    if aud not in valid_auds:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "invalid aud",
                "description": "FAM only proxies userinfo requests for FAM tokens",
            },
        )

    return JSONResponse(content=jsonable_encoder(decoded_payload))


@router.get("/jwks.json", status_code=200)
def bcsc_jwks(request: Request):

    key = kms_lookup._bcsc_public_key

    key_value_bytes = key["PublicKey"]
    pub_key_dec = b64encode(key_value_bytes).decode()

    algorithm = "RS256"
    e = "AQAB"
    kid = "bcscencryption"
    kty = "RSA"
    n = pub_key_dec
    use = "enc"

    jwks_dict = {
        "keys": [{"alg": algorithm, "e": e, "kid": kid, "kty": kty, "n": n, "use": use}]
    }

    return JSONResponse(content=jwks_dict)


async def get_body(request: Request):
    return await request.body()


# key = RSA.generate(2048)
# private_key = key.export_key('PEM')
# public_key = key.publickey().exportKey('PEM')
# imported_private_key = RSA.importKey(private_key)
# rsa_private_key = PKCS1_OAEP.new(imported_private_key)
# imported_public_key = RSA.importKey(public_key)
# rsa_public_key = PKCS1_OAEP.new(imported_public_key)


@router.post("/encryption_test", status_code=200)
def encryption_test(body: bytes = Depends(get_body)):

    # Receive an encrypted message, unencrypt it, and send it back

    LOGGER.info(f"Request body is: [{body}]")

    decoded_data = b64decode(body)

    LOGGER.info(f"Decoded data is: [{decoded_data}")

    decrypted_data = kms_lookup.decrypt(decoded_data)
    # decrypted_data = rsa_private_key.decrypt(decoded_data)

    return Response(content=decrypted_data, media_type="text/plain")


@router.post("/encryption_test_test", status_code=200)
def encryption_test_test(body: bytes = Depends(get_body)):

    # Read the body, encode it, and send it to encryption test

    # encrypted_text = rsa_public_key.encrypt(body)

    encrypted_text = kms_lookup.encrypt(body)

    emsg = b64encode(encrypted_text)

    test_url = (
        "http://localhost:8000/bcsc/encryption_test"
    )

    # test_url = (
    #     "https://qz39ajtria.execute-api.ca-central-1.amazonaws.com/v1/bcsc/encryption_test"
    # )

    raw_response = requests.post(url=test_url, data=emsg).text

    return Response(content=raw_response, media_type="text/plain")
