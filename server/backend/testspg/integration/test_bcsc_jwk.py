"""
Characterization tests for the BCSC JWK key classes.

`bcsc_jwk` is the layer that touches `cryptography` most directly - AES
`Cipher`/`modes`, `aead.AESGCM`, `PKCS7` padding and `InvalidTag`. These tests
pin the current behaviour so a `cryptography` upgrade is verified against real
encrypt/decrypt results.

Like `test_bcsc_decryption.py` these are pure unit tests: no database, no
network, no environment variables, no patching of global state.
"""

import base64
import logging

import pytest
from api.app.integration.bcsc import bcsc_jwk
from api.app.integration.bcsc.bcsc_constants import JWEError, JWKError
from api.app.integration.bcsc.bcsc_jwk import CryptographyAESKey, HMACKey
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, aead, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7

LOGGER = logging.getLogger(__name__)

CBC_IV = bytes(range(16))
GCM_IV = bytes(range(12))


def aes_cbc_encrypt(key: bytes, iv: bytes, plain_text: bytes) -> bytes:
    """Encrypt with PKCS7 padding using `cryptography` directly."""
    padder = PKCS7(algorithms.AES.block_size).padder()
    padded = padder.update(plain_text) + padder.finalize()
    encryptor = Cipher(
        algorithms.AES(key), modes.CBC(iv), backend=default_backend()
    ).encryptor()
    return encryptor.update(padded) + encryptor.finalize()


def aes_gcm_encrypt(key: bytes, iv: bytes, plain_text: bytes, aad: bytes):
    """Returns (cipher_text, auth_tag) with the trailing 16-byte GCM tag split off."""
    cipher_text_and_tag = aead.AESGCM(key).encrypt(iv, plain_text, aad)
    return cipher_text_and_tag[:-16], cipher_text_and_tag[-16:]


class TestJwkConstruct:

    @pytest.mark.parametrize("algorithm", ["HS256", "HS384", "HS512"])
    def test_hmac_algorithms_build_hmac_key(self, algorithm):
        key = bcsc_jwk.jwk_construct(b"a-shared-secret", algorithm)

        assert isinstance(key, HMACKey)

    @pytest.mark.parametrize(
        "algorithm, key_len",
        [
            ("A128CBC", 16),
            ("A192CBC", 24),
            ("A256CBC", 32),
            ("A128GCM", 16),
            ("A128CBC-HS256", 32),
            ("A192CBC-HS384", 48),
            ("A256CBC-HS512", 64),
        ],
    )
    def test_aes_algorithms_build_aes_key(self, algorithm, key_len):
        key = bcsc_jwk.jwk_construct(bytes(key_len), algorithm)

        assert isinstance(key, CryptographyAESKey)

    def test_algorithm_is_read_from_jwk_dict(self):
        secret = b"a-shared-secret"
        jwk_dict = {
            "alg": "HS256",
            "kty": "oct",
            "k": base64.urlsafe_b64encode(secret).replace(b"=", b"").decode(),
        }

        key = bcsc_jwk.jwk_construct(jwk_dict)

        assert isinstance(key, HMACKey)
        assert key.prepared_key == secret

    def test_missing_algorithm_is_rejected(self):
        with pytest.raises(JWKError, match="Unable to find an algorithm"):
            bcsc_jwk.jwk_construct(b"a-shared-secret")

    @pytest.mark.parametrize("algorithm", ["NOT-AN-ALGORITHM", "A128GCMKW", "RSA-OAEP"])
    def test_unsupported_algorithm_is_rejected(self, algorithm):
        with pytest.raises(JWKError, match="Unable to find an algorithm"):
            bcsc_jwk.jwk_construct(bytes(32), algorithm)


class TestHMACKey:

    def test_sign_and_verify_round_trip(self):
        key = bcsc_jwk.jwk_construct(b"a-shared-secret", "HS256")
        message = b"bcsc-auth-tag-input"

        signature = key.sign(message)

        assert len(signature) == 32
        assert key.verify(message, signature) is True

    def test_verify_rejects_wrong_signature(self):
        key = bcsc_jwk.jwk_construct(b"a-shared-secret", "HS256")

        assert key.verify(b"bcsc-auth-tag-input", b"not-the-signature") is False

    def test_verify_rejects_tampered_message(self):
        key = bcsc_jwk.jwk_construct(b"a-shared-secret", "HS256")
        signature = key.sign(b"bcsc-auth-tag-input")

        assert key.verify(b"bcsc-auth-tag-inpuT", signature) is False

    def test_str_key_is_encoded_as_utf8(self):
        assert (
            bcsc_jwk.jwk_construct("a-shared-secret", "HS256").prepared_key
            == b"a-shared-secret"
        )

    @pytest.mark.parametrize(
        "key",
        [
            b"-----BEGIN PUBLIC KEY-----\nMIIB\n-----END PUBLIC KEY-----",
            b"-----BEGIN RSA PUBLIC KEY-----\nMIIB\n-----END RSA PUBLIC KEY-----",
            b"-----BEGIN CERTIFICATE-----\nMIIB\n-----END CERTIFICATE-----",
            b"ssh-rsa AAAAB3Nza",
        ],
    )
    def test_asymmetric_key_material_is_rejected_as_hmac_secret(self, key):
        with pytest.raises(JWKError, match="asymmetric key or x509 certificate"):
            bcsc_jwk.jwk_construct(key, "HS256")

    def test_non_string_key_is_rejected(self):
        with pytest.raises(JWKError, match="Expecting a string- or bytes-formatted key"):
            bcsc_jwk.jwk_construct(12345, "HS256")

    def test_non_hmac_algorithm_is_rejected(self):
        with pytest.raises(JWKError, match="not a valid hash algorithm"):
            HMACKey(b"a-shared-secret", "RS256")

    def test_jwk_dict_with_wrong_key_type_is_rejected(self):
        with pytest.raises(JWKError, match="Incorrect key type"):
            bcsc_jwk.jwk_construct({"alg": "HS256", "kty": "RSA", "k": "AAAA"})

    def test_to_dict_round_trips_through_jwk_construct(self):
        secret = b"a-shared-secret"
        original = bcsc_jwk.jwk_construct(secret, "HS256")

        rebuilt = bcsc_jwk.jwk_construct(original.to_dict())

        assert rebuilt.prepared_key == secret


class TestCryptographyAESKeyLengthValidation:

    @pytest.mark.parametrize(
        "algorithm, valid_len, expected_bits",
        [
            ("A128CBC", 16, "128"),
            ("A192CBC", 24, "192"),
            ("A256CBC", 32, "256"),
            ("A192CBC-HS384", 48, "384"),
            ("A256CBC-HS512", 64, "512"),
        ],
    )
    def test_wrong_key_length_is_rejected(self, algorithm, valid_len, expected_bits):
        with pytest.raises(JWKError, match=f"Key must be {expected_bits} bit"):
            CryptographyAESKey(bytes(valid_len - 1), algorithm)

    def test_non_aes_algorithm_is_rejected(self):
        with pytest.raises(JWKError, match="not a valid AES algorithm"):
            CryptographyAESKey(bytes(32), "HS256")


class TestCryptographyAESKeyCbcDecrypt:

    @pytest.mark.parametrize(
        "length",
        # Around the AES 16-byte block boundary, where PKCS7 padding breaks first.
        [0, 1, 15, 16, 17, 31, 32, 33],
    )
    def test_decrypt_unpads_correctly(self, length):
        key_bytes = bytes((i * 3 + 1) % 256 for i in range(16))
        plain_text = b"y" * length
        cipher_text = aes_cbc_encrypt(key_bytes, CBC_IV, plain_text)

        key = bcsc_jwk.jwk_construct(key_bytes, "A128CBC")

        assert key.decrypt(cipher_text, CBC_IV) == plain_text

    def test_decrypt_with_wrong_key_is_rejected(self):
        key_bytes = bytes((i * 3 + 1) % 256 for i in range(16))
        cipher_text = aes_cbc_encrypt(key_bytes, CBC_IV, b"a" * 32)

        key = bcsc_jwk.jwk_construct(bytes(16), "A128CBC")

        # Garbage plaintext fails PKCS7 unpadding.
        with pytest.raises(JWEError):
            key.decrypt(cipher_text, CBC_IV)

    def test_decrypt_with_non_block_aligned_cipher_text_is_rejected(self):
        key = bcsc_jwk.jwk_construct(bytes(16), "A128CBC")

        with pytest.raises(JWEError):
            key.decrypt(b"not-a-whole-block", CBC_IV)


class TestCryptographyAESKeyGcmDecrypt:

    def test_decrypt_round_trip(self):
        key_bytes = bytes((i * 5 + 2) % 256 for i in range(16))
        plain_text = b'{"sub":"test-bcsc-subject"}'
        aad = b"protected-header"
        cipher_text, tag = aes_gcm_encrypt(key_bytes, GCM_IV, plain_text, aad)

        key = bcsc_jwk.jwk_construct(key_bytes, "A128GCM")

        assert key.decrypt(cipher_text, GCM_IV, aad, tag) == plain_text

    def test_tampered_auth_tag_is_rejected(self):
        key_bytes = bytes((i * 5 + 2) % 256 for i in range(16))
        aad = b"protected-header"
        cipher_text, tag = aes_gcm_encrypt(key_bytes, GCM_IV, b"payload", aad)
        tampered_tag = bytes([tag[0] ^ 0x01]) + tag[1:]

        key = bcsc_jwk.jwk_construct(key_bytes, "A128GCM")

        with pytest.raises(JWEError, match="Invalid JWE Auth Tag"):
            key.decrypt(cipher_text, GCM_IV, aad, tampered_tag)

    def test_tampered_aad_is_rejected(self):
        key_bytes = bytes((i * 5 + 2) % 256 for i in range(16))
        cipher_text, tag = aes_gcm_encrypt(
            key_bytes, GCM_IV, b"payload", b"protected-header"
        )

        key = bcsc_jwk.jwk_construct(key_bytes, "A128GCM")

        with pytest.raises(JWEError, match="Invalid JWE Auth Tag"):
            key.decrypt(cipher_text, GCM_IV, b"different-header", tag)

    def test_missing_auth_tag_is_rejected(self):
        key_bytes = bytes((i * 5 + 2) % 256 for i in range(16))
        cipher_text, _tag = aes_gcm_encrypt(key_bytes, GCM_IV, b"payload", b"aad")

        key = bcsc_jwk.jwk_construct(key_bytes, "A128GCM")

        with pytest.raises(JWEError, match="tag cannot be None"):
            key.decrypt(cipher_text, GCM_IV, b"aad", None)
