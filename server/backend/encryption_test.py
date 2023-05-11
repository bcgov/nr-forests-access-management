import json
from urllib.request import urlopen
import logging
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from base64 import b64decode, b64encode
from jose import jws, jwt
from jose.utils import base64url_decode, base64url_encode
from jose.exceptions import JWSError, JWSSignatureError
import binascii
from collections.abc import Iterable, Mapping
import requests
from api import jwe

LOGGER = logging.getLogger(__name__)

# jwks = requests.get('https://qz39ajtria.execute-api.ca-central-1.amazonaws.com/v1/bcsc/jwks.json').text
# json_response = json.loads(jwks)
# keytext = json_response["keys"][0]["n"]
# key_unencoded = base64url_decode(keytext)


# public_key_text = '''-----BEGIN PUBLIC KEY-----
# MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2YIo5DqGD1ehHEOtLok8
# 1j1aP6wtxZkOjXr6fYHHTtaniDFODQwp+hlFMJw3hkjrnTm1xLp67pRX4wIwXhu3
# sdZhMr90NEW+vC7XKkf4Yz+2v37omzUCmk23BLhR8yzwJr87Q7oLumIEUvx729Z6
# yDg+KxjCNlObUbXy+1xazTmBiJly0HbXxXP+nFIOwZXaHGLCJfqZ535lL6UCX80W
# tNu0IpPcOQXlSRrlWaMs09O5Gj5bTdvSqkp9cuMBPK3/ZfXYgOBY7DsGuK4Hw98Q
# jNQyJK2f+ENkHcM3RIHnDUzXbB/9d5IESS6o8rkR8mhylhLtaJAget5vH1huFiym
# cQIDAQAB
# -----END PUBLIC KEY-----'''

header = "eyJraWQiOiJiY3NjZW5jcnlwdGlvbiIsImN0eSI6IkpXVCIsImVuYyI6IkEyNTZDQkMtSFM1MTIiLCJhbGciOiJSU0EtT0FFUC0yNTYifQ"
emcrypted_key = "ZOpWA7GV59DvUCUHS9f7XF-zNlPU4vQ_FK27cNxIhkxBkzZVIruV6hwWwNCQv5gKUyZH_PfOZMFC9x3XL-CpzEuIZb5uZgEAbR43u_7vEOdkhsoNemRU4HAneFJVZ4fLu3RYMWPsV4mqbB1XBnauTa6MvpYJ_8I17Mf2xPT-Fq3JhkvUUI3xId64W_olb2t6H4_Woc2qG3rPTPhRu_bHqciVDZCd8xNOnrIQYT9C5FXUlLnkT-JNb27oZOplaOxzbY2W8xvDaMdyLUP9DiefDGNEtJN1YLBE62Bq3w3Kx86k7lNlZWA316oLH1mliUtGtjUS2YP-g0CcC6PbuXVdug"
what_is_this_thing = "wR6jkjcqUsTDN54MjNd-Kg"
encrypted_message = "VfwYCg8RIcxSH46lrronWzvydrOi73-rvMWqUgxl4mZIvyP7ieO8tDk9RGfuEpNYHdryeqtFGz1dTWS0WUOrU054Z5VDkkOmcLvQQdC4yZ8rCLE-TTQrHhGfLMnzU3Dk_aSuNY2dhipY66fNm66G-5REzRbtKvudi7GbIBp4mFRop_wMvCJWKUEdDGJVML-Ed3fZ6oHKpy7YGxV0ZUCxBzg37SNwaUuxqeimc27XgjOA23oyo9qbFLhvr6yPlguBBMvWzDUys9VNjQkpmXyKY_HXmozhJ34PwltsJqCIFU1dbRZhUPCF2wHxPxuSbVvcDYMjD4u6H4AwGbFC6A5EGkpsTmS0T54dQqV8rmyoULCGvWhMLxT0ejqtKdQEfobg7siEqnFIxqifY1MyBvda9w7qvlOPSaWkHGKTPhUxDiaSYX5F5zhQzK04c5oIwZVhqPMGIL_GNHjL3Qwp4buWwXdxE-XHGQXeMZXR6hSbcFRs9x1sg8lw9yRzQlay_zX2c2Vilv2nH48EJ41gIVtBPO7MKxUaI8B6U6yb56WJd5Bag9G0KArfXdmjU9L08QQB0GMqupXAdOsyC6TnTF2CneVi2xmD5sEn91Jwn_Kv-HOr_EXkCmwZy4KWli5PrbrQg0AyOrs9O0DvwBizuStXoPbmS2KA8bay03qPhQCpuPf7cv2YcmQ8Fd0ev_MYksICGhMCaIyvdzPa9M5WfmhvlWm8bkcNZEt-XvjzJwMqvLHfz306HSO0FfJptROoKpmU0u2L13PLr2z1B0OWIzZWQlXy01ZYBwrS80UlXftZs9oISiwGqILYXI3IIsyMfusrHa9NJDE_MBChUdZUlpcjtBQMa0MNNsRBO2VGwUbOPKC1tDavph49M9AyuzuUObJ24TDu0jauiIX7cYo6Z9yUhkSxDy6ThQhNDetZb987wziVTyE_qzu5yIaiIJ4l-gwGdtKYBhL86IQ0rPQ12bc99BzQQSeeC6RHdzO-T8OgjGM.umDISyAzA0XSpd7Sz8O-mF06MCkQPkQ7DdgvS27ND7s"

unencrypted_key = "cEbVYTQY6rPuc9zJKFDhKha8Nk/W90HHfeOqWvvKLnuANDfm/f0A5mL0iEcbS2uKa/oSJR1ZN+7BUEOQuH5a/Q=="
key_unencoded = base64url_decode(unencrypted_key)

enc = "A256CBC-HS512"

# Decrypt the message using the unencrypted key

id_token = 'eyJraWQiOiJiY3NjZW5jcnlwdGlvbiIsImN0eSI6IkpXVCIsImVuYyI6IkEyNTZDQkMtSFM1MTIiLCJhbGciOiJSU0EtT0FFUC0yNTYifQ.ZOpWA7GV59DvUCUHS9f7XF-zNlPU4vQ_FK27cNxIhkxBkzZVIruV6hwWwNCQv5gKUyZH_PfOZMFC9x3XL-CpzEuIZb5uZgEAbR43u_7vEOdkhsoNemRU4HAneFJVZ4fLu3RYMWPsV4mqbB1XBnauTa6MvpYJ_8I17Mf2xPT-Fq3JhkvUUI3xId64W_olb2t6H4_Woc2qG3rPTPhRu_bHqciVDZCd8xNOnrIQYT9C5FXUlLnkT-JNb27oZOplaOxzbY2W8xvDaMdyLUP9DiefDGNEtJN1YLBE62Bq3w3Kx86k7lNlZWA316oLH1mliUtGtjUS2YP-g0CcC6PbuXVdug.wR6jkjcqUsTDN54MjNd-Kg.VfwYCg8RIcxSH46lrronWzvydrOi73-rvMWqUgxl4mZIvyP7ieO8tDk9RGfuEpNYHdryeqtFGz1dTWS0WUOrU054Z5VDkkOmcLvQQdC4yZ8rCLE-TTQrHhGfLMnzU3Dk_aSuNY2dhipY66fNm66G-5REzRbtKvudi7GbIBp4mFRop_wMvCJWKUEdDGJVML-Ed3fZ6oHKpy7YGxV0ZUCxBzg37SNwaUuxqeimc27XgjOA23oyo9qbFLhvr6yPlguBBMvWzDUys9VNjQkpmXyKY_HXmozhJ34PwltsJqCIFU1dbRZhUPCF2wHxPxuSbVvcDYMjD4u6H4AwGbFC6A5EGkpsTmS0T54dQqV8rmyoULCGvWhMLxT0ejqtKdQEfobg7siEqnFIxqifY1MyBvda9w7qvlOPSaWkHGKTPhUxDiaSYX5F5zhQzK04c5oIwZVhqPMGIL_GNHjL3Qwp4buWwXdxE-XHGQXeMZXR6hSbcFRs9x1sg8lw9yRzQlay_zX2c2Vilv2nH48EJ41gIVtBPO7MKxUaI8B6U6yb56WJd5Bag9G0KArfXdmjU9L08QQB0GMqupXAdOsyC6TnTF2CneVi2xmD5sEn91Jwn_Kv-HOr_EXkCmwZy4KWli5PrbrQg0AyOrs9O0DvwBizuStXoPbmS2KA8bay03qPhQCpuPf7cv2YcmQ8Fd0ev_MYksICGhMCaIyvdzPa9M5WfmhvlWm8bkcNZEt-XvjzJwMqvLHfz306HSO0FfJptROoKpmU0u2L13PLr2z1B0OWIzZWQlXy01ZYBwrS80UlXftZs9oISiwGqILYXI3IIsyMfusrHa9NJDE_MBChUdZUlpcjtBQMa0MNNsRBO2VGwUbOPKC1tDavph49M9AyuzuUObJ24TDu0jauiIX7cYo6Z9yUhkSxDy6ThQhNDetZb987wziVTyE_qzu5yIaiIJ4l-gwGdtKYBhL86IQ0rPQ12bc99BzQQSeeC6RHdzO-T8OgjGM.umDISyAzA0XSpd7Sz8O-mF06MCkQPkQ7DdgvS27ND7s'

decrypted_token = jwe.decrypt(id_token, unencrypted_key)



# rsa_public_key = RSA.importKey(public_key_text)
# rsa_public_key = PKCS1_OAEP.new(key=rsa_public_key, hashAlgo=SHA256)
# encrypted_text = rsa_public_key.encrypt(b'Yo yo bum rush the show')
# b64_encoded_text = base64url_encode(encrypted_text)
# print(b64_encoded_text)

# decoded = base64url_decode(b'HKuMkq3xKg6q6trlJv2dEhioZKwhB4EVPUU1IpZvXQ-O0MoEW9vpVVXZ7sqqz3Oal1dlWOj2Pwp55a9VVBndwyHv3DyvyEZvFLxoaqUlEZzKJ4eApgGvS7SEq2nqhYQFQL-ceJeUQjHKaiyvq6zZKjbXjT1Qalvq5ZrqLuYhumTGyDEgqJtz6r35-puZVOrEAAvdOWlSNIdXeXvM9cOUPJrx-2DB01hque8Ek9YI-v-sB9pFqP2RCqRszmoiEzsxhb4Mz6ZvQEWb3SuJqWvt1u5-I_iF0jtRwA92mRT4wrWLtmewgcKVznpVV6PRkS7B7mUzeaUuBFsZ2GyC3vcMQ8qlc2vQur996IgtnrkFVnkQPP5n58x-_SoqwBy0k_JRdxk6LQmL')
# print(b64encode(decoded))


# if isinstance(encoded_id_token, str):
#     token = encoded_id_token.encode("utf-8")
# try:
#     signing_input, crypto_segment = token.rsplit(b".", 1)
#     header_segment, claims_segment = signing_input.split(b".", 1)
#     header_data = base64url_decode(header_segment)
# except ValueError:
#     raise JWSError("Not enough segments")
# except (TypeError, binascii.Error):
#     raise JWSError("Invalid header padding")

# try:
#     header = json.loads(header_data.decode("utf-8"))
# except ValueError as e:
#     raise JWSError("Invalid header string: %s" % e)

# if not isinstance(header, Mapping):
#     raise JWSError("Invalid header string: must be a json object")

# try:
#     payload = base64url_decode(claims_segment)
# except (TypeError, binascii.Error):
#     raise JWSError("Invalid payload padding")

# try:
#     signature = base64url_decode(crypto_segment)
# except (TypeError, binascii.Error):
#     raise JWSError("Invalid crypto padding")



# id_token_encrypted_payload = jws.verify(
#     token=encoded_id_token,
#     key=None,
#     algorithms="RS256",
#     verify=False
# )


# key = RSA.generate(2048)
# private_key = key.export_key('PEM')
# public_key = key.publickey().exportKey('PEM')
# message = input('plain text for RSA encryption and decryption:')
# message = str.encode(message)

# rsa_public_key = RSA.importKey(public_key)
# rsa_public_key = PKCS1_OAEP.new(rsa_public_key)
# encrypted_text = rsa_public_key.encrypt(message)

# print('your encrypted_text is : {}'.format(encrypted_text))

# rsa_private_key = RSA.importKey(private_key)
# rsa_private_key = PKCS1_OAEP.new(rsa_private_key)
# decrypted_text = rsa_private_key.decrypt(encrypted_text)

# print('your decrypted_text is : {}'.format(decrypted_text))

# try:
#     jwks = None

#     url = "https://qz39ajtria.execute-api.ca-central-1.amazonaws.com/v1/bcsc/jwks.json"
#     with urlopen(url) as response:
#         jwks = json.loads(response.read().decode("utf-8"))

# except Exception as e:
#     LOGGER.error(f"init_jwks function failed to reach AWS: {e}.")
#     LOGGER.error("Backend API will not work properly.")
#     raise e

# jwk = {}
# for key in jwks["keys"]:
#     if key["kid"] == "bcscencryption":
#         jwk = {
#             "kty": key["kty"],
#             "kid": key["kid"],
#             "use": key["use"],
#             "n": key["n"],
#             "e": key["e"],
#         }
#     break

# LOGGER.warning(jwk)

# pubkey = jwk["n"]

# msg = "1000 Monkeys"
# keyDER = b64decode(pubkey)
# keyPub = RSA.importKey(keyDER)
# cipher = PKCS1_OAEP.new(keyPub)
# cipher_text = cipher.encrypt(msg.encode())
# emsg = b64encode(cipher_text)

# LOGGER.warning(emsg)

# test_url = (
#     "https://qz39ajtria.execute-api.ca-central-1.amazonaws.com/v1/bcsc/encryption_test"
# )

# raw_response = None

# with urlopen(test_url, data=emsg) as response:
#     raw_response = response.read().decode("utf-8")

# LOGGER.warning(raw_response)
