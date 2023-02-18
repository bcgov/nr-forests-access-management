import json
import os
import time

import pytest
from jose import jws

COGNITO_REGION = os.environ.get('COGNITO_REGION')
COGNITO_USER_POOL_ID = os.environ.get('COGNITO_USER_POOL_ID')
COGNITO_CLIENT_ID = os.environ.get('COGNITO_CLIENT_ID')
COGNITO_USER_POOL_DOMAIN = os.environ.get('COGNITO_USER_POOL_DOMAIN')


def create_jwt_access_claims():
    return {
        "sub": "51b661cf-4109-4616-b7a5-178daf51fc12",
        "cognito:groups": [
            "FAM_ACCESS_ADMIN"
        ],
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
        "username": "idir_b5ecdb094dfb4149a6a8445a01a96bf0@idir"
    }


def create_jwt_id_claims():
    return {
        "sub": "e8c217e4-2c0e-45b6-9c5a-fff43c60c3ff",
        "cognito:groups": [ "FOM_REVIEWER" ],
        "custom:idp_name": "idir",
        "iss": "https://cognito-idp.ca-central-1.amazonaws.com/ca-central-1_yds9Vci8g",
        "cognito:username": "dev-idir_e72a12c916a44a9581cf39e5dcdffae7@idir",
        "nonce": "APBEWsGN2ke1UCEiBrHGD1dNjXiU6rym-SCSm8UaQwaiqP5py5dML8fimxPiqEHLznhQrVTZ2bf1pMtrBxdKpKIwSG0WwGlpjj9eqsEEAq2v-weHTFxLgHep_VuWkPVIhCTRhpYPViy0An7hD0gqj7CUVzsEfAnFxpwocvKOqX8",
        "custom:idp_user_id": "E72A12C916A44A9581CF39E5DCDFFAE7",
        "origin_jti": "3658423e-c74a-4610-96c2-fb81abd0566a",
        "aud": "6c9ieu27ik29mq75jeb7rrbdls",
        "custom:idp_username": "IANLIU",
        "token_use": "id",
        "auth_time": time.time(),
        "custom:idp_display_name": "Liu, Ian WLRS:EX",
        "exp": time.time() + 60000,
        "iat": time.time(),
        "jti": "0945ff00-74a0-401e-83a6-5f8049655186",
        "email": "ian.liu@gov.bc.ca"
    }

def create_jwt_id_token(test_rsa_key,
                        claims=create_jwt_id_claims(),
                        test_algorithm="RS256",
                        test_headers={"kid": "12345"}):
    return jws.sign(claims, test_rsa_key, algorithm=test_algorithm,
                    headers=test_headers)


def create_jwt_access_token(test_rsa_key,
                            claims=create_jwt_access_claims(),
                            test_algorithm='RS256',
                            test_headers={"kid": "12345"}):
    return jws.sign(claims, test_rsa_key, algorithm=test_algorithm,
                    headers=test_headers)


def assert_error_response(response, http_error_code, error_code_string):
    assert response.status_code == http_error_code, f"Expected status code {http_error_code} but received {response.status_code}"
    error_detail_code = json.loads(response.text)['detail']['code']
    assert error_detail_code == error_code_string, f"Expected error detail.code {error_code_string} but received {error_detail_code}"


def headers(id_token, access_token):
    # python str() to single quote, need to enclose it to double quote JSON standard string.
    token = str({"id_token": id_token, "access_token": access_token}).replace("'", "\"")
    return {"Authorization": f"Bearer {token}"}
