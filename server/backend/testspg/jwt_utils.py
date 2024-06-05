import os
from jose import jws
import time
import json

COGNITO_REGION = os.environ.get("COGNITO_REGION")
COGNITO_USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID")
COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID")
COGNITO_USER_POOL_DOMAIN = os.environ.get("COGNITO_USER_POOL_DOMAIN")

IDP_USER_GUID = "B5ECDB094DFB4149A6A8445A0MANGLED"
COGNITO_USERNAME = "test-idir_b5ecdb094dfb4149a6a8445a0mangled@idir"
IDIR_USERNAME = "COGUSTAF"

# Users setup (key identifier: cognito_user_id) for testing purpose.
# We added these user "TEST-3-LOAD-CHILD-1"(BCEID) and "PTOLLEST"(IDIR) as
#   FOM DEV delegated admin in local flyway sql, to manage role for
#   FOM REVIEWER and FOM SUBMITTER with forest client number 00001018
COGNITO_USERNAME_BCEID_DELEGATED_ADMIN = (
    # "TEST-3-LOAD-CHILD-1"(BCEID)
    "test-bceidbusiness_bda2a1e212244dc2b9f9522057mangledc58bbb@bceidbusiness"
)
COGNITO_USERNAME_IDIR_DELEGATED_ADMIN = (
    # "PTOLLEST"(IDIR)
    "test-idir_eb65e9d7828d4718aa6f4193cmangled@idir"
)


def create_jwt_claims():
    return {
        "sub": "51b661cf-4109-4616-b7a5-178daf51fc12",
        "cognito:groups": ["FAM_ADMIN"],
        "iss": f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}",
        "version": 2,
        "client_id": COGNITO_CLIENT_ID,
        "origin_jti": "9aac7342-78ca-471b-a027-9f6daf3b923b",
        "token_use": "access",
        "scope": "openid profile",
        "auth_time": time.time(),
        "exp": time.time() + 60000,
        "iat": time.time(),
        "jti": "6ab8647c-0679-4d25-a71a-2400966fea9a",
        "username": COGNITO_USERNAME,
    }


def create_jwt_token(
    test_rsa_key,
    roles=["FAM_ADMIN"],
    username=COGNITO_USERNAME,
    claims=create_jwt_claims(),
    test_algorithm="RS256",
    test_headers={"kid": "12345"},
):
    if roles is not None:
        claims["cognito:groups"] = roles
    claims["username"] = username
    return jws.sign(
        claims, test_rsa_key, algorithm=test_algorithm, headers=test_headers
    )


def assert_error_response(response, http_error_code, error_code_string):
    assert (
        response.status_code == http_error_code
    ), f"Expected status code {http_error_code} but received {response.status_code}"
    error_detail_code = json.loads(response.text)["detail"]["code"]
    assert (
        error_detail_code == error_code_string
    ), f"Expected error detail.code {error_code_string} but received {error_detail_code}"


def headers(token):
    return {"Authorization": f"Bearer {token}"}
