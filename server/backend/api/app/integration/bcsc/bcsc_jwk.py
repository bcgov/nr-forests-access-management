import base64
import hashlib
import hmac

from api.app.integration.bcsc.bcsc_constants import ALGORITHMS
from api.app.utils.utils import base64url_decode
from jose import jwk

# This code partial is from "python-jose" not maintained library.
# https://pypi.org/project/python-jose/


def jwk_construct(key_data, algorithm=None):
    """
    Construct a Key object for the given algorithm with the given
    key_data.
    """

    # Allow for pulling the algorithm off of the passed in jwk.
    if not algorithm and isinstance(key_data, dict):
        algorithm = key_data.get("alg", None)

    if not algorithm:
        raise JWKError("Unable to find an algorithm for key: %s" % key_data)

    key_class = jwk.get_key(algorithm)
    if not key_class:
        raise JWKError("Unable to find an algorithm for key: %s" % key_data)
    return key_class(key_data, algorithm)


class JOSEError(Exception):
    pass


class JWKError(JOSEError):
    pass


def get_key(algorithm):
    if algorithm in ALGORITHMS.KEYS:
        return ALGORITHMS.KEYS[algorithm]
    elif algorithm in ALGORITHMS.HMAC:  # noqa: F811
        return HMACKey
    # elif algorithm in ALGORITHMS.RSA:
    #     from jose.backends import RSAKey  # noqa: F811

    #     return RSAKey
    # elif algorithm in ALGORITHMS.EC:
    #     from jose.backends import ECKey  # noqa: F811

    #     return ECKey
    elif algorithm in ALGORITHMS.AES:
        from jose.backends import AESKey  # noqa: F811

        return AESKey
    # elif algorithm == ALGORITHMS.DIR:
    #     from jose.backends import DIRKey  # noqa: F811

    #     return DIRKey
    return None


class Key:
    """
    A simple interface for implementing JWK keys.
    """

    def __init__(self, key, algorithm):
        pass

    def sign(self, msg):
        raise NotImplementedError()

    def verify(self, msg, sig):
        raise NotImplementedError()

    def public_key(self):
        raise NotImplementedError()

    def to_pem(self):
        raise NotImplementedError()

    def to_dict(self):
        raise NotImplementedError()

    def encrypt(self, plain_text, aad=None):
        """
        Encrypt the plain text and generate an auth tag if appropriate

        Args:
            plain_text (bytes): Data to encrypt
            aad (bytes, optional): Authenticated Additional Data if key's algorithm supports auth mode

        Returns:
            (bytes, bytes, bytes): IV, cipher text, and auth tag
        """
        raise NotImplementedError()

    def decrypt(self, cipher_text, iv=None, aad=None, tag=None):
        """
        Decrypt the cipher text and validate the auth tag if present
        Args:
            cipher_text (bytes): Cipher text to decrypt
            iv (bytes): IV if block mode
            aad (bytes): Additional Authenticated Data to verify if auth mode
            tag (bytes): Authentication tag if auth mode

        Returns:
            bytes: Decrypted value
        """
        raise NotImplementedError()

    def wrap_key(self, key_data):
        """
        Wrap the the plain text key data

        Args:
            key_data (bytes): Key data to wrap

        Returns:
            bytes: Wrapped key
        """
        raise NotImplementedError()

    def unwrap_key(self, wrapped_key):
        """
        Unwrap the the wrapped key data

        Args:
            wrapped_key (bytes): Wrapped key data to unwrap

        Returns:
            bytes: Unwrapped key
        """
        raise NotImplementedError()


class HMACKey(Key):
    """
    Performs signing and verification operations using HMAC
    and the specified hash function.
    """

    HASHES = {ALGORITHMS.HS256: hashlib.sha256, ALGORITHMS.HS384: hashlib.sha384, ALGORITHMS.HS512: hashlib.sha512}

    def __init__(self, key, algorithm):
        if algorithm not in ALGORITHMS.HMAC:
            raise JWKError("hash_alg: %s is not a valid hash algorithm" % algorithm)
        self._algorithm = algorithm
        self._hash_alg = self.HASHES.get(algorithm)

        if isinstance(key, dict):
            self.prepared_key = self._process_jwk(key)
            return

        if not isinstance(key, str) and not isinstance(key, bytes):
            raise JWKError("Expecting a string- or bytes-formatted key.")

        if isinstance(key, str):
            key = key.encode("utf-8")

        invalid_strings = [
            b"-----BEGIN PUBLIC KEY-----",
            b"-----BEGIN RSA PUBLIC KEY-----",
            b"-----BEGIN CERTIFICATE-----",
            b"ssh-rsa",
        ]

        if any(string_value in key for string_value in invalid_strings):
            raise JWKError(
                "The specified key is an asymmetric key or x509 certificate and"
                " should not be used as an HMAC secret."
            )

        self.prepared_key = key

    def _process_jwk(self, jwk_dict):
        if not jwk_dict.get("kty") == "oct":
            raise JWKError("Incorrect key type. Expected: 'oct', Received: %s" % jwk_dict.get("kty"))

        k = jwk_dict.get("k")
        k = k.encode("utf-8")
        k = bytes(k)
        k = base64url_decode(k)

        return k

    def sign(self, msg):
        return hmac.new(self.prepared_key, msg, self._hash_alg).digest()

    def verify(self, msg, sig):
        return hmac.compare_digest(sig, self.sign(msg))

    def to_dict(self):
        return {
            "alg": self._algorithm,
            "kty": "oct",
            "k": base64url_encode(self.prepared_key).decode("ASCII"),
        }


def base64url_encode(input):
    """Helper method to base64url_encode a string.

    Args:
        input (str): A base64url_encoded string to encode.

    """
    return base64.urlsafe_b64encode(input).replace(b"=", b"")