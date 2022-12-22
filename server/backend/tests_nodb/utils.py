from jose import jws
import time
import json


def create_jwt_claims():
    return {
        "sub": "51b661cf-4109-4616-b7a5-178daf51fc12",
        "cognito:groups": [
            "FAM_ADMIN"
        ],
        "iss": "https://cognito-idp.ca-central-1.amazonaws.com/ca-central-1_5BOn4rGL8",
        "version": 2,
        "client_id": "26tltjjfe7ktm4bte7av998d78",
        "origin_jti": "9aac7342-78ca-471b-a027-9f6daf3b923b",
        "token_use": "access",
        "scope": "openid profile",
        "auth_time": time.time(),
        "exp": time.time() + 60000,
        "iat": time.time(),
        "jti": "6ab8647c-0679-4d25-a71a-2400966fea9a",
        "username": "idir_b5ecdb094dfb4149a6a8445a01a96bf0@idir"
    }


def create_jwt_token(test_rsa_key,
                     claims=create_jwt_claims(),
                     test_algorithm='RS256',
                     test_headers={"kid": "12345"}):
    return jws.sign(claims, test_rsa_key, algorithm=test_algorithm,
                    headers=test_headers)


def assert_error_response(response, http_error_code, error_code_string):
    assert response.status_code == http_error_code, f"Expected status code {http_error_code} but received {response.status_code}"
    error_detail_code = json.loads(response.text)['detail']['code']
    assert error_detail_code == error_code_string, f"Expected error detail.code {error_code_string} but received {error_detail_code}"

