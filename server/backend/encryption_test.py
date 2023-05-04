import json
from urllib.request import urlopen
import logging
from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Cipher import PKCS1_OAEP
from base64 import b64decode, b64encode
from jose import jws, jwt
from jose.utils import base64url_decode, base64url_encode
from jose.exceptions import JWSError, JWSSignatureError
import binascii
from collections.abc import Iterable, Mapping

LOGGER = logging.getLogger(__name__)

token = "eyJraWQiOiJiY3NjZW5jcnlwdGlvbiIsImN0eSI6IkpXVCIsImVuYyI6IkEyNTZDQkMtSFM1MTIiLCJhbGciOiJSU0EtT0FFUC0yNTYifQ.BhkhA3czNFY3DmmASMWNTwHQDbhaUMGT4I1SFh_a5qp5tCPMvWIGzRg6-8VMVjDTk0FZ_v5pakGDZ88Gv1GRLdsh7dLZ7e-lysoVPu-zgs4llXFQmeCfK9CtkOK-zrl6khXXVb-ZK6fg6NvScO6ZaGuYD3mYQ03hVF8cBXnv8Joc8G04R7PGHVoySZQyzwbkKA-7XOICLJFclaV6wwvHQiEfq7VOHvanNKjdlvm1Noahh9eUBrGN7jPlby_78yQDDclgD-42KyOpZePbhP0WL71Zshqg2X2rei5JBPKrmHClCyZ0FSf_GQZ6sCSCG9Yq7YaVjwOSEgDsxU42ohTIILhan9qOMFQqKIlNNAGEet7mU2UcOX3x0UL7ueqNGISw7gP-AXOF.sY5DqBWKfFpiweTvBVlRvQ.s-35BQgGQzE7T1yDd4yVojqRS5YKP2TYvz7jPEVZ6rPGvra1EKBSxjciQjYQ941iYrjIT4Mazbfeqt-gF2MbXNr_x_tteMHKA8LFXivG4usCT9c4uDAF8__iwOXOVdpmmqBfKXKKAf3_0uJj7na9lvyU6f4QS762IBtzvhx72C753Oh83wuNVagVDCXNWrfTaDSLmtNvpljbZNIUd6r4uomY7YuUInuofhDywTA7z6SYbKtgDMSegPCmzKTwalsXdhH-mI8P5DrhH3bi4swgHacL0jmCjhTL8mETQMjegxAWpIeslpsKVVB0hvorvmSN3HlA9UjVAdkT07jQtARh9cBZeuje01Ols6s-HWsAj01pknn55d7HSoqxa3TrRbyIxrP8GfGN_DFHCMbA8hM1FvB6VCImgbmzC6vBxuVrPqw7I1v5fWrnmJ0dd7ezw-P7jyrXBGLI1g6DR1p5gfvnH4nnxJ02sJS0BgCHLxSYCFOl5j9Iq019ij7x5N7Y1Fbv_pLqYiV979EMOSgYuGpxqH6Nj5kjA1PF3cvsm1SoW9ivtLASnypBKGBgaV5OSNfXTWxtWHAnJML5GoNDgbarztiGk3O4xM-fBdBYDTwUDyLalbp0cGWu5A5dcfQMqMxprXapw7a2yZ6i_H6F6Y3-FM6wcU6_qhiAbEpqRLkUGbG4dL_UzeOLfWcHaLPHBhuu0K9HtkH5TPQuFXxfiJXDWp7ij5mAa9ocPRK22BRtbBCtqC87oTBwjts60_EM08rS8Mx703mh24bfPZnuYPbAB0w1IasyKQJyE4NBLYXEP8pNC3Ss4dfHkK6MQLE0Qac1wi9uU6D9SV5FYtWQY0Sfu7KQxTNIZWLiIV6TYMwqTc2YaB9I1sGqGrkuViuiH0Gsf8LoXVDyPV4LK3DEfHfOvGgGm2vUgauNz_gvwio98t58VyMwOP8XOuPr9TIAtMDg15ELyCDURThvknPMT9_qMCXWKTAVRnN-LKNKDUJoY_g.UyUhInFcCIDwYYtQqUVjJsVmjcwINcnuXg0GU8YGgDg"

signing_input, crypto_segment = token.rsplit('.', 1)
header_segment, claims_segment = signing_input.split('.', 1)

# print(claims_segment)

public_key_text = '''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2YIo5DqGD1ehHEOtLok8
1j1aP6wtxZkOjXr6fYHHTtaniDFODQwp+hlFMJw3hkjrnTm1xLp67pRX4wIwXhu3
sdZhMr90NEW+vC7XKkf4Yz+2v37omzUCmk23BLhR8yzwJr87Q7oLumIEUvx729Z6
yDg+KxjCNlObUbXy+1xazTmBiJly0HbXxXP+nFIOwZXaHGLCJfqZ535lL6UCX80W
tNu0IpPcOQXlSRrlWaMs09O5Gj5bTdvSqkp9cuMBPK3/ZfXYgOBY7DsGuK4Hw98Q
jNQyJK2f+ENkHcM3RIHnDUzXbB/9d5IESS6o8rkR8mhylhLtaJAget5vH1huFiym
cQIDAQAB
-----END PUBLIC KEY-----'''

rsa_public_key = RSA.importKey(public_key_text)
rsa_public_key = PKCS1_OAEP.new(rsa_public_key, "RSAES_OAEP_SHA_256")
encrypted_text = rsa_public_key.encrypt(b'Yo yo bum rush the show')
b64_encoded_text = b64encode(encrypted_text)
print(b64_encoded_text)


# print(b64encode(b'BhkhA3czNFY3DmmASMWNTwHQDbhaUMGT4I1SFh_a5qp5tCPMvWIGzRg6-8VMVjDTk0FZ_v5pakGDZ88Gv1GRLdsh7dLZ7e-lysoVPu-zgs4llXFQmeCfK9CtkOK-zrl6khXXVb-ZK6fg6NvScO6ZaGuYD3mYQ03hVF8cBXnv8Joc8G04R7PGHVoySZQyzwbkKA-7XOICLJFclaV6wwvHQiEfq7VOHvanNKjdlvm1Noahh9eUBrGN7jPlby_78yQDDclgD-42KyOpZePbhP0WL71Zshqg2X2rei5JBPKrmHClCyZ0FSf_GQZ6sCSCG9Yq7YaVjwOSEgDsxU42ohTIILhan9qOMFQqKIlNNAGEet7mU2UcOX3x0UL7ueqNGISw7gP-AXOF'))


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
