import base64
import hashlib
import hmac
import logging

from api.app.integration.bcsc.bcsc_constants import (ALGORITHMS, JWEError,
                                                     JWKError)
from api.app.utils import utils
from api.app.utils.utils import base64url_decode
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import (Cipher, aead, algorithms,
                                                    modes)
from cryptography.hazmat.primitives.padding import PKCS7

LOGGER = logging.getLogger(__name__)

# This code partial is from "python-jose" not maintained library.
# https://pypi.org/project/python-jose/, please see notes at
# bcsc_dscryption.py.


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

    key_class = get_key(algorithm)
    LOGGER.debug(f"key_class: {key_class}")
    if not key_class:
        raise JWKError("Unable to find an algorithm for key: %s" % key_data)
    return key_class(key_data, algorithm)


# BCSC uses HMAC and AES for now. Comment out conditions to
# be easier to be ported.
def get_key(algorithm):
    if algorithm in ALGORITHMS.KEYS:
        return ALGORITHMS.KEYS[algorithm]
    elif algorithm in ALGORITHMS.HMAC:  # noqa: F811
        return HMACKey
    elif algorithm in ALGORITHMS.AES:  # noqa: F811
        return CryptographyAESKey
    """
    # elif algorithm in ALGORITHMS.RSA:
    #     from jose.backends import RSAKey  # noqa: F811

    #     return RSAKey
    # elif algorithm in ALGORITHMS.EC:
    #     from jose.backends import ECKey  # noqa: F811

    #     return ECKey
    # elif algorithm == ALGORITHMS.DIR:
    #     from jose.backends import DIRKey  # noqa: F811

    #     return DIRKey
    """
    return None


class Key:
    """
    A simple interface for implementing JWK keys.
    """

    def __init__(self, key, algorithm):
        pass  # sonar fix: this is library code interface.

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


class CryptographyAESKey(Key):
    KEY_128 = (ALGORITHMS.A128GCM, ALGORITHMS.A128GCMKW, ALGORITHMS.A128KW, ALGORITHMS.A128CBC)
    KEY_192 = (ALGORITHMS.A192GCM, ALGORITHMS.A192GCMKW, ALGORITHMS.A192KW, ALGORITHMS.A192CBC)
    KEY_256 = (
        ALGORITHMS.A256GCM,
        ALGORITHMS.A256GCMKW,
        ALGORITHMS.A256KW,
        ALGORITHMS.A128CBC_HS256,
        ALGORITHMS.A256CBC,
    )
    KEY_384 = (ALGORITHMS.A192CBC_HS384,)
    KEY_512 = (ALGORITHMS.A256CBC_HS512,)

    AES_KW_ALGS = (ALGORITHMS.A128KW, ALGORITHMS.A192KW, ALGORITHMS.A256KW)

    MODES = {
        ALGORITHMS.A128GCM: modes.GCM,
        ALGORITHMS.A192GCM: modes.GCM,
        ALGORITHMS.A256GCM: modes.GCM,
        ALGORITHMS.A128CBC_HS256: modes.CBC,
        ALGORITHMS.A192CBC_HS384: modes.CBC,
        ALGORITHMS.A256CBC_HS512: modes.CBC,
        ALGORITHMS.A128CBC: modes.CBC,
        ALGORITHMS.A192CBC: modes.CBC,
        ALGORITHMS.A256CBC: modes.CBC,
        ALGORITHMS.A128GCMKW: modes.GCM,
        ALGORITHMS.A192GCMKW: modes.GCM,
        ALGORITHMS.A256GCMKW: modes.GCM,
        ALGORITHMS.A128KW: None,
        ALGORITHMS.A192KW: None,
        ALGORITHMS.A256KW: None,
    }

    def __init__(self, key, algorithm):
        if algorithm not in ALGORITHMS.AES:
            raise JWKError("%s is not a valid AES algorithm" % algorithm)
        if algorithm not in ALGORITHMS.SUPPORTED.union(ALGORITHMS.AES_PSEUDO):
            raise JWKError("%s is not a supported algorithm" % algorithm)

        self._algorithm = algorithm
        self._mode = self.MODES.get(self._algorithm)

        if algorithm in self.KEY_128 and len(key) != 16:
            raise JWKError(f"Key must be 128 bit for alg {algorithm}")
        elif algorithm in self.KEY_192 and len(key) != 24:
            raise JWKError(f"Key must be 192 bit for alg {algorithm}")
        elif algorithm in self.KEY_256 and len(key) != 32:
            raise JWKError(f"Key must be 256 bit for alg {algorithm}")
        elif algorithm in self.KEY_384 and len(key) != 48:
            raise JWKError(f"Key must be 384 bit for alg {algorithm}")
        elif algorithm in self.KEY_512 and len(key) != 64:
            raise JWKError(f"Key must be 512 bit for alg {algorithm}")

        self._key = key

    def to_dict(self):
        data = {"alg": self._algorithm, "kty": "oct", "k": base64url_encode(self._key)}
        return data

    # Commented out, no encryption is needed for FAM-BCSC.
    # def encrypt(self, plain_text, aad=None):
    #     plain_text = utils.ensure_binary(plain_text)
    #     try:
    #         iv = get_random_bytes(algorithms.AES.block_size // 8)
    #         mode = self._mode(iv)
    #         if mode.name == "GCM":
    #             cipher = aead.AESGCM(self._key)
    #             cipher_text_and_tag = cipher.encrypt(iv, plain_text, aad)
    #             cipher_text = cipher_text_and_tag[: len(cipher_text_and_tag) - 16]
    #             auth_tag = cipher_text_and_tag[-16:]
    #         else:
    #             cipher = Cipher(algorithms.AES(self._key), mode, backend=default_backend())
    #             encryptor = cipher.encryptor()
    #             padder = PKCS7(algorithms.AES.block_size).padder()
    #             padded_data = padder.update(plain_text)
    #             padded_data += padder.finalize()
    #             cipher_text = encryptor.update(padded_data) + encryptor.finalize()
    #             auth_tag = None
    #         return iv, cipher_text, auth_tag
    #     except Exception as e:
    #         raise JWEError(e)

    def decrypt(self, cipher_text, iv=None, aad=None, tag=None):
        cipher_text = utils.ensure_binary(cipher_text)
        try:
            iv = utils.ensure_binary(iv)
            mode = self._mode(iv)
            if mode.name == "GCM":
                if tag is None:
                    raise ValueError("tag cannot be None")
                cipher = aead.AESGCM(self._key)
                cipher_text_and_tag = cipher_text + tag
                try:
                    plain_text = cipher.decrypt(iv, cipher_text_and_tag, aad)
                except InvalidTag:
                    raise JWEError("Invalid JWE Auth Tag")
            else:
                cipher = Cipher(algorithms.AES(self._key), mode, backend=default_backend())
                decryptor = cipher.decryptor()
                padded_plain_text = decryptor.update(cipher_text)
                padded_plain_text += decryptor.finalize()
                unpadder = PKCS7(algorithms.AES.block_size).unpadder()
                plain_text = unpadder.update(padded_plain_text)
                plain_text += unpadder.finalize()

            return plain_text
        except Exception as e:
            raise JWEError(e)

    # Commented out, no encryption is needed for FAM-BCSC.
    # def wrap_key(self, key_data):
    #     key_data = utils.ensure_binary(key_data)
    #     cipher_text = aes_key_wrap(self._key, key_data, default_backend())
    #     return cipher_text  # IV, cipher text, auth tag

    # Commented out, no encryption is needed for FAM-BCSC.
    # def unwrap_key(self, wrapped_key):
    #     wrapped_key = utils.ensure_binary(wrapped_key)
    #     try:
    #         plain_text = aes_key_unwrap(self._key, wrapped_key, default_backend())
    #     except InvalidUnwrap as cause:
    #         raise JWEError(cause)
    #     return plain_text


def base64url_encode(input):
    """Helper method to base64url_encode a string.

    Args:
        input (str): A base64url_encoded string to encode.

    """
    return base64.urlsafe_b64encode(input).replace(b"=", b"")