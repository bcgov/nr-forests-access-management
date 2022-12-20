import logging
import starlette.testclient
from api.app.main import apiPrefix
import jose
from time import time
# from Crypto.PublicKey import RSA

LOGGER = logging.getLogger(__name__)
endPoint = f"{apiPrefix}/fam_applications"


def test_get_application_noauthentication_failure(
        test_client_fixture: starlette.testclient.TestClient):
    response = test_client_fixture.get(endPoint)
    LOGGER.debug(f"endPoint: {endPoint}")
    LOGGER.debug(f"response {response}")
    assert response.status_code == 401


def test_get_application_bad_token_failure(
        test_client_fixture: starlette.testclient.TestClient):

    response = test_client_fixture.get(f"{endPoint}", headers={"Authorization": "Bearer 12345"})
    LOGGER.debug(f"endPoint: {endPoint}")
    LOGGER.debug(f"response {response}")
    assert response.status_code == 401


def test_get_application_success(
        test_client_fixture: starlette.testclient.TestClient):

    # Only works if you drop a valid token in here manually!
    response = test_client_fixture.get(f"{endPoint}", headers={"Authorization": "Bearer eyJraWQiOiJGTk44Qkh0bXNnb0JXdW9IOFhZS3p2K25QZVB5VnIrb3RcL0d6RFNLaVdPRT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI1MWI2NjFjZi00MTA5LTQ2MTYtYjdhNS0xNzhkYWY1MWZjMTIiLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAuY2EtY2VudHJhbC0xLmFtYXpvbmF3cy5jb21cL2NhLWNlbnRyYWwtMV81Qk9uNHJHTDgiLCJ2ZXJzaW9uIjoyLCJjbGllbnRfaWQiOiIyNnRsdGpqZmU3a3RtNGJ0ZTdhdjk5OGQ3OCIsIm9yaWdpbl9qdGkiOiJmZmY1ZjRhYi04ZWRiLTQ1YjgtYTNjZS01NDUyNDEwMzAyYzQiLCJ0b2tlbl91c2UiOiJhY2Nlc3MiLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIiwiYXV0aF90aW1lIjoxNjcxMjM5NTc3LCJleHAiOjE2NzEyNDMxNzcsImlhdCI6MTY3MTIzOTU4MCwianRpIjoiNmYyZjRhZTctYjAyMi00YzZmLTkzNDUtMGFhMTUwMTU3NTE2IiwidXNlcm5hbWUiOiJpZGlyX2I1ZWNkYjA5NGRmYjQxNDlhNmE4NDQ1YTAxYTk2YmYwQGlkaXIifQ.vl6dSkuEGoMd0WPUHlPE88ikpuqxUkPuj1Krm257zfBSUgm_YTeeN3u8YltbxwyxikLG3ev6dxEW3v259H5tgctbEXgtSuqeEQ9OAb4HBCD9QVpdpKr_jw6_2BBjmiXupHZo4p6sBjFRgU6JukayTf-x62Vavnbx62HFhs7oUkoi7LrBWXeMNJjh89eY9g-zWz_VxeHI3Gwf8UzyZoxCNijzFgps6OUdFT5EFt6RBe0BwJ1oPd5-MlFLnHGTurtTZ-x-32NsQYlEavVi2-iQTS6uiUfV4VCdVN7ceYRRLE-Rlt8EL2H-R5KoNOfGvw1ABgwqI6kkh-JvS2gVCgKQFg"})
    LOGGER.debug(f"endPoint: {endPoint}")
    LOGGER.debug(f"response {response}")
    assert response.status_code == 204
    data = response.json()
    LOGGER.debug(f"data: {data}")
    assert data == []


# def test_create_test_jwt():
#     # key for demonstration purposes
#     key = RSA.generate(2048)

#     claims = {
#         'iss': 'http://www.example.com',
#         'exp': int(time()) + 3600,
#         'sub': 42,
#     }

#     # encrypt claims using the public key
#     pub_jwk = {'k': key.publickey().exportKey('PEM')}

#     jwe = jose.encrypt(claims, pub_jwk)
#     jwt = jose.serialize_compact(jwe)


#     # decrypt on the other end using the private key
#     priv_jwk = {'k': key.exportKey('PEM')}

#     jwt = jose.decrypt(jose.deserialize_compact(jwt), priv_jwk)




# def test_get_application_invalid_signature_failure
# def test_get_application_bad_issuer
# def test_get_application_bad_client
# def test_get_application_wrong_alg
# def test_get_application_missing_kid
