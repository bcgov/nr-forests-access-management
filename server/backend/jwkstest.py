from authlib.jose import JsonWebKey

public_key_text = '''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2YIo5DqGD1ehHEOtLok8
1j1aP6wtxZkOjXr6fYHHTtaniDFODQwp+hlFMJw3hkjrnTm1xLp67pRX4wIwXhu3
sdZhMr90NEW+vC7XKkf4Yz+2v37omzUCmk23BLhR8yzwJr87Q7oLumIEUvx729Z6
yDg+KxjCNlObUbXy+1xazTmBiJly0HbXxXP+nFIOwZXaHGLCJfqZ535lL6UCX80W
tNu0IpPcOQXlSRrlWaMs09O5Gj5bTdvSqkp9cuMBPK3/ZfXYgOBY7DsGuK4Hw98Q
jNQyJK2f+ENkHcM3RIHnDUzXbB/9d5IESS6o8rkR8mhylhLtaJAget5vH1huFiym
cQIDAQAB
-----END PUBLIC KEY-----'''

algorithm = "RS256"
e = "AQAB"
kid = "bcscencryption"
kty = "RSA"
use = "enc"
params = {"alg": algorithm, "e": e, "kid": kid, "kty": kty, "use": use}

key = JsonWebKey.import_key(public_key_text, params)
print(key.as_json())