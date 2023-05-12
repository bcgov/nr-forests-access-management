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
from api.app import jwe

LOGGER = logging.getLogger(__name__)


jwe_token = 'eyJraWQiOiJiY3NjZW5jcnlwdGlvbiIsImN0eSI6IkpXVCIsImVuYyI6IkEyNTZDQkMtSFM1MTIiLCJhbGciOiJSU0EtT0FFUC0yNTYifQ.n9QZMOIOd4pngJEd1ego6LOTQNMRklDAuMzF4Eufk-MKCTOl40vfRtIwdhAXU9gAU50mNp0O2skcUY2zhj7LwWEjRxrgW4NTrhQE_3yQ0thzDzAEFEN5mHHS5vVgwocHm6mZgh9APdlu2Mh2t5CZRqguRXM5Mn3oA1PsCZCKDdwAptZU2aGVKP9V4gcIoqGpRT9MCIxm4QkRKea7xsPhC31vrcaB1fwM4p-FvyvScnuoYVv8NmXQNO1xI9a85gtDLSGzev7RVM5hYyy-4Ua1Gi-A7tMe2558Lrcnu1H4VKmOWIZf5buL96y95-n-lbepbNjnimFyRETJUtL-2QRLCA.tYZ2cNECC5FTMM-6vetxMQ.f6HMfIG4nTw4oTUN16GggF8BbvJMp6BWWmJvNjnI8wevRPgQcArBxQeDnxp6x35-2oVzFHUViAeDCpAPpcb6AWlxX66VMvRR_WjXEexp0e_mZDhBXi39mqO-Q8Axp0RqiF0oEuAUTsqAumBy0EwP17cL-V_YsMDbfFsFgdRT2kscsk3VPPCQZhd6Hy2bPHyTPoMeBxyuWHFC2BW3EmMMuQtl61nhhdnV6lyWcFS4XEB70fxpfgEF4sEkOXjDSdN3nzBRCGZeaHUNLcbc_IPlHfs_oQ6ezN-CG_2p7hUX5jXhY0cRVtp7P-Wah1QEnAKWc6S13UkrKeaqGssPVLHrv9VjKo6Yg-e69MdACq9qca5nfdncKaazY7oZyUMPjtJG54yZnIUTyNqVDnaW56qX0YLzCg6IbzxvgIhtsqtUT_UNJJnUwpRr1BbIJAvFVfRyBxpRoL1QSGgER3aQkYu0N-1YseLGcKJAlJkZQKt5HF2AvstB8v-7R4apmHjn0iseqWFAzCrgsCsZyIsp1z7aUq-nve01RBTgrMvSAzppWNSLlx3vOJMX8zrlcDrQuPk5xHqX0QmVvgZhg_4_qUMPf9bFOAspZAGjRjd26q8bywe9fLapxJrgByGHWpysrUJckvKkU-f8g4LOgS35Jjo0lC7hCCt_-bd-Rh05YyTQfnV40yMs7WBMoeXRx2GhAGu-PpLZQwz3m9r31ajF251bMCQ8XwkUtT2KBSDOhzgDAb3uuCAXeX8k3eyBCVLAI77VZMpZ_ABDs2SVwPVIe9zwpb-JwtZstbARCRVRvMZd2GM0jpdUusOjO2qc2Qr1E79qICcDxSRkUwLwujD_5iUUS0QdBUHXr1raZUd1PHkWp5WabLsJV5T-WZaUz7QS33vF6ln0fwRjjq8SbbffTK_D_A1fKOb3N3YKiVAeRCbQ2HjYO1rcayh_FxOA0E3BwfJ8qZV_7IpGc28I2eCWr0prsTeme05dBRIYk0E-2Mg-5NAIGmok4feG97nS2faKygPPX-7NMUasobrEdU0zuLqyreIXelyqL6G1XnqrsQcaL-kii_3iKmHprXdf-eM59ldwAcr2SSXQxcJdDJUrp65QgNQymGHrDC49yRy7uDT4gQ1tBCRxYQPVm727_ZxcsAjuxt6KljFnlYe29S9N8knNeDbalaE7sbX05Ix7gILR1vE_Vn7w5J9WjvmmeturggpUEL4eGhgBPw3BCn9XZ-OFXdzkptc7YIYLItj2dKfJfMqR-dfD16WZfPKnIkiRwGndgD6vPwsiijF9-0MNlee7grCTE1sKX0p2PfYZUuHGPPk.kr5kSkbVj_dvQJQuvf-yY8TLCewFd5VBXorkLU0uZa4'

encrypted_key_segment = jwe_token.split(".", 4)[1]

decrypt_url = "https://qz39ajtria.execute-api.ca-central-1.amazonaws.com/v1/bcsc/decryption_test"
encoded_decrypted_key = requests.post(url=decrypt_url, data=encrypted_key_segment).text
as_bytes = bytes(encoded_decrypted_key, 'utf-8')
decrypted_key = base64url_decode(as_bytes)

decrypted_token = jwe.decrypt(jwe_token, decrypted_key)

print(f"jwe_token: [{jwe_token}]")
print(f"encrypted_key_segment: [{encrypted_key_segment}]")
print(f"encoded_decrypted_key: [{encoded_decrypted_key}]")
print(f"as_bytes: [{as_bytes}]")
print(f"decrypted_key: [{decrypted_key}]")



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