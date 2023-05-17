from authlib.jose import JsonWebKey
from base64 import b64decode, b64encode
from jose.utils import base64url_decode, base64url_encode
from jose import jwk
from cryptography.hazmat.primitives import serialization as crypto_serialization

public_key_text = '''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2YIo5DqGD1ehHEOtLok8
1j1aP6wtxZkOjXr6fYHHTtaniDFODQwp+hlFMJw3hkjrnTm1xLp67pRX4wIwXhu3
sdZhMr90NEW+vC7XKkf4Yz+2v37omzUCmk23BLhR8yzwJr87Q7oLumIEUvx729Z6
yDg+KxjCNlObUbXy+1xazTmBiJly0HbXxXP+nFIOwZXaHGLCJfqZ535lL6UCX80W
tNu0IpPcOQXlSRrlWaMs09O5Gj5bTdvSqkp9cuMBPK3/ZfXYgOBY7DsGuK4Hw98Q
jNQyJK2f+ENkHcM3RIHnDUzXbB/9d5IESS6o8rkR8mhylhLtaJAget5vH1huFiym
cQIDAQAB
-----END PUBLIC KEY-----'''

key_value_bytes = b'0\x82\x01"0\r\x06\t*\x86H\x86\xf7\r\x01\x01\x01\x05\x00\x03\x82\x01\x0f\x000\x82\x01\n\x02\x82\x01\x01\x00\xd9\x82(\xe4:\x86\x0fW\xa1\x1cC\xad.\x89<\xd6=Z?\xac-\xc5\x99\x0e\x8dz\xfa}\x81\xc7N\xd6\xa7\x881N\r\x0c)\xfa\x19E0\x9c7\x86H\xeb\x9d9\xb5\xc4\xbaz\xee\x94W\xe3\x020^\x1b\xb7\xb1\xd6a2\xbft4E\xbe\xbc.\xd7*G\xf8c?\xb6\xbf~\xe8\x9b5\x02\x9aM\xb7\x04\xb8Q\xf3,\xf0&\xbf;C\xba\x0b\xbab\x04R\xfc{\xdb\xd6z\xc88>+\x18\xc26S\x9bQ\xb5\xf2\xfb\\Z\xcd9\x81\x88\x99r\xd0v\xd7\xc5s\xfe\x9cR\x0e\xc1\x95\xda\x1cb\xc2%\xfa\x99\xe7~e/\xa5\x02_\xcd\x16\xb4\xdb\xb4"\x93\xdc9\x05\xe5I\x1a\xe5Y\xa3,\xd3\xd3\xb9\x1a>[M\xdb\xd2\xaaJ}r\xe3\x01<\xad\xffe\xf5\xd8\x80\xe0X\xec;\x06\xb8\xae\x07\xc3\xdf\x10\x8c\xd42$\xad\x9f\xf8Cd\x1d\xc37D\x81\xe7\rL\xd7l\x1f\xfdw\x92\x04I.\xa8\xf2\xb9\x11\xf2hr\x96\x12\xedh\x90 z\xdeo\x1fXn\x16,\xa6q\x02\x03\x01\x00\x01'
public_key = crypto_serialization.load_der_public_key(key_value_bytes)

# print(key_value_bytes)
# print(pub_key_dec)

# jwk.construct(pub_key_dec)

# as_bytes = bytes(pub_key_dec, 'utf-8')
# decrypted_key = base64url_decode(as_bytes)



algorithm = "RS256"
e = "AQAB"
kid = "bcscencryption"
kty = "RSA"
use = "enc"
params = {"alg": algorithm, "e": e, "kid": kid, "kty": kty, "use": use}

key = JsonWebKey.import_key(public_key_text, params)
print(key.as_json())


