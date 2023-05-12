import logging
from fastapi import APIRouter, Request, Response, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import requests
from jose import jwt
from fastapi import HTTPException
from .. import kms_lookup
import json
from jose.utils import base64url_decode, base64url_encode
from api import jwe

LOGGER = logging.getLogger(__name__)

router = APIRouter()


async def get_body(request: Request):
    return await request.body()


@router.post("/token/dev", status_code=200)
def bcsc_token_dev(request: Request, body: bytes = Depends(get_body)):
    return bcsc_token(request, "https://idtest.gov.bc.ca/oauth2/token", body)


@router.post("/token/test", status_code=200)
def bcsc_token_test(request: Request, body: bytes = Depends(get_body)):
    return bcsc_token(request, "https://idtest.gov.bc.ca/oauth2/token", body)


@router.post("/token/prod", status_code=200)
def bcsc_token_prod(request: Request, body: bytes = Depends(get_body)):
    return bcsc_token(request, "https://id.gov.bc.ca/oauth2/token", body)


def bcsc_token(request: Request, bcsc_token_uri, body):

    """
    Proxy the BCSC token endpoint and decode the result
    """

    LOGGER.debug(f"Request params: [{request.query_params}]")

    response = requests.post(url=bcsc_token_uri, headers=request.headers, data=body)

    raw_response = response.text

    LOGGER.debug(f"Raw response is: [{raw_response}]")

    json_response = json.loads(raw_response)

    # Remove the id token from the token response
    # Cognito doesn't use it anyway and when it is a JWE it causes a Cognito error
    del json_response['id_token']

    return Response(content=json.dumps(json_response), media_type="application/json")


@router.get("/userinfo/dev", status_code=200)
def bcsc_userinfo_dev(request: Request):
    return bcsc_userinfo(request, "https://idtest.gov.bc.ca/oauth2/userinfo")


@router.get("/userinfo/test", status_code=200)
def bcsc_userinfo_test(request: Request):
    return bcsc_userinfo(request, "https://idtest.gov.bc.ca/oauth2/userinfo")


@router.get("/userinfo/prod", status_code=200)
def bcsc_userinfo_prod(request: Request):
    return bcsc_userinfo(request, "https://id.gov.bc.ca/oauth2/userinfo")


def bcsc_userinfo(request: Request, bcsc_userinfo_uri):

    """
    Proxy the BCSC userinfo endpoint and decode the result
    """

    jwe_token = requests.get(url=bcsc_userinfo_uri, headers=request.headers).text

    ################### Begin Decryption Stuff ##########################

    # When the result is a JWE, you have to get the encrypted key from the JWE
    # and then unencrypt it to be able to use it to unencrypt the payload

    # Ensure binary input
    if isinstance(jwe_token, str):
        jwe_token = jwe_token.encode("utf-8", "strict")
    elif not isinstance(jwe_token, bytes):
        raise TypeError(f"not expecting type '{type(jwe_token)}'")

    # Get the second segment of the token to get the cek
    encrypted_key_segment = jwe_token.split(b".", 4)[1]

    # In local mode, call AWS to do the decryption
    # decrypt_url = "https://qz39ajtria.execute-api.ca-central-1.amazonaws.com/v1/bcsc/decryption_test"
    # encoded_decrypted_key = requests.post(url=decrypt_url, data=encrypted_key_segment).text
    # as_bytes = bytes(encoded_decrypted_key, 'utf-8')
    # decrypted_key = base64url_decode(as_bytes)

    # In AWS Decode and decrypt the cek (only works in AWS because kms code)
    decoded_key = base64url_decode(encrypted_key_segment)
    decrypted_key = kms_lookup.decrypt(decoded_key)

    # Use the symmetric public key to decrypt the payload
    decrypted_id_token = jwe.decrypt(jwe_token, decrypted_key)

    decoded_id_token = jwt.decode(
        decrypted_id_token, None, options={"verify_signature": False, "verify_aud": False}
    )

    aud = decoded_id_token["aud"]
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

    return JSONResponse(content=jsonable_encoder(decoded_id_token))


@router.get("/jwks.json", status_code=200)
def bcsc_jwks(request: Request):

    # key = kms_lookup._bcsc_public_key

    # key_value_bytes = key["PublicKey"]
    # pub_key_dec = base64url_encode(key_value_bytes).decode()

    # Used this website: https://tribestream.io/tools/pem2jwk/
    # To convert the public key value to JWKS value
    key_from_website = "2YIo5DqGD1ehHEOtLok81j1aP6wtxZkOjXr6fYHHTtaniDFODQwp-hlFMJw3hkjrnTm1xLp67pRX4wIwXhu3sdZhMr90NEW-vC7XKkf4Yz-2v37omzUCmk23BLhR8yzwJr87Q7oLumIEUvx729Z6yDg-KxjCNlObUbXy-1xazTmBiJly0HbXxXP-nFIOwZXaHGLCJfqZ535lL6UCX80WtNu0IpPcOQXlSRrlWaMs09O5Gj5bTdvSqkp9cuMBPK3_ZfXYgOBY7DsGuK4Hw98QjNQyJK2f-ENkHcM3RIHnDUzXbB_9d5IESS6o8rkR8mhylhLtaJAget5vH1huFiymcQ"

    algorithm = "RS256"
    e = "AQAB"
    kid = "bcscencryption"
    kty = "RSA"
    n = key_from_website
    use = "enc"

    jwks_dict = {
        "keys": [{"alg": algorithm, "e": e, "kid": kid, "kty": kty, "n": n, "use": use}]
    }

    return JSONResponse(content=jwks_dict)



# key = RSA.generate(2048)
# private_key = key.export_key('PEM')
# public_key = key.publickey().exportKey('PEM')
# imported_private_key = RSA.importKey(private_key)
# rsa_private_key = PKCS1_OAEP.new(imported_private_key)
# imported_public_key = RSA.importKey(public_key)
# rsa_public_key = PKCS1_OAEP.new(imported_public_key)


@router.post("/encryption_test", status_code=200)
def decryption_test_test(body: bytes = Depends(get_body)):

    encrypted_data = kms_lookup.encrypt(body)
    encoded_data = base64url_encode(encrypted_data)
    return Response(content=encoded_data, media_type="text/plain")


@router.post("/decryption_test", status_code=200)
def decryption_test(body: bytes = Depends(get_body)):

    # Receive an encrypted message, unencrypt it, and send it back

    decoded_data = base64url_decode(body)
    decrypted_data = kms_lookup.decrypt(decoded_data)
    return Response(content=base64url_encode(decrypted_data), media_type="text/plain")


#     # Read the body, encrypt and encode it, send it back

#     # encrypted_text = rsa_public_key.encrypt(body)



#     # encrypted_text = kms_lookup.encrypt(body)

#     # emsg = b64encode(encrypted_text)

#     # test_url = (
#     #     "http://localhost:8000/bcsc/encryption_test"
#     # )

#     # test_url = (
#     #     "https://qz39ajtria.execute-api.ca-central-1.amazonaws.com/v1/bcsc/encryption_test"
#     # )

#     # raw_response = requests.post(url=test_url, data=emsg).text

#     decoded_data = b64decode(emsg)
#     decrypted_data = kms_lookup.decrypt(decoded_data)
#     # decrypted_data = rsa_private_key.decrypt(decoded_data)

#     return Response(content=decrypted_data, media_type="text/plain")

#     # return Response(content=raw_response, media_type="text/plain")
