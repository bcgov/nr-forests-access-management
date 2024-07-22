import binascii
import json
import logging
from collections.abc import Mapping
from struct import pack

from api.app.integration.bcsc import bcsc_jwk
from api.app.integration.bcsc.bcsc_constants import (ALGORITHMS, JWEError,
                                                     JWEParseError)
from api.app.utils import utils

LOGGER = logging.getLogger(__name__)


def decrypt(jwe_str, decrypted_key):
    """Decrypts a JWE compact serialized string and returns the plaintext.

    Args:
        jwe_str (str): A JWE to be decrypt.
        key (str or dict): A key to attempt to decrypt the payload with. Can be
            individual JWK or JWK set.

    Returns:
        bytes: The plaintext bytes, assuming the authentication tag is valid.

    Raises:
        JWEError: If there is an exception verifying the token.

    Examples:
        >>> from jose import jwe
        >>> jwe.decrypt(jwe_string, 'asecret128bitkey')
        'Hello, World!'
    """
    header, encoded_header, encrypted_key, iv, cipher_text, auth_tag = _jwe_compact_deserialize(jwe_str)

    try:
        # Determine the Key Management Mode employed by the algorithm
        # specified by the "alg" (algorithm) Header Parameter.
        alg = header["alg"]
        enc = header["enc"]
        if alg not in ALGORITHMS.SUPPORTED:
            raise JWEError("Algorithm %s not supported." % alg)
        if enc not in ALGORITHMS.SUPPORTED:
            raise JWEError("Algorithm %s not supported." % enc)
    except KeyError:
        raise JWEParseError("alg and enc headers are required!")


    # Compute the Encoded Protected Header value BASE64URL(UTF8(JWE
    # Protected Header)).  If the JWE Protected Header is not present
    # (which can only happen when using the JWE JSON Serialization and
    # no "protected" member is present), let this value be the empty
    # string.
    protected_header = encoded_header

    # Let the Additional Authenticated Data encryption parameter be
    # ASCII(Encoded Protected Header).  However, if a JWE AAD value is
    # present (which can only be the case when using the JWE JSON
    # Serialization), instead let the Additional Authenticated Data
    # encryption parameter be ASCII(Encoded Protected Header || '.' ||
    # BASE64URL(JWE AAD)).
    aad = protected_header

    # Decrypt the JWE Ciphertext using the CEK, the JWE Initialization
    # Vector, the Additional Authenticated Data value, and the JWE
    # Authentication Tag (which is the Authentication Tag input to the
    # calculation) using the specified content encryption algorithm,
    # returning the decrypted plaintext and validating the JWE
    # Authentication Tag in the manner specified for the algorithm,
    # rejecting the input without emitting any decrypted output if the
    # JWE Authentication Tag is incorrect.
    try:
        plain_text = _decrypt_and_auth(decrypted_key, enc, cipher_text, iv, aad, auth_tag)
    except NotImplementedError:
        raise JWEError(f"enc {enc} is not implemented")
    except Exception as e:
        raise JWEError(e)

    return plain_text


def get_unverified_header(jwe_str):
    """Returns the decoded headers without verification of any kind.

    Args:
        jwe_str (str): A compact serialized JWE to decode the headers from.

    Returns:
        dict: The dict representation of the JWE headers.

    Raises:
        JWEError: If there is an exception decoding the JWE.
    """
    header = _jwe_compact_deserialize(jwe_str)[0]
    return header


def _decrypt_and_auth(cek_bytes, enc, cipher_text, iv, aad, auth_tag):
    """
    Decrypt and verify the data

    Args:
        cek_bytes (bytes): cek to derive encryption and possible auth key to
            verify the auth tag
        cipher_text (bytes): Encrypted data
        iv (bytes): Initialization vector (iv) used to encrypt data
        aad (bytes): Additional Authenticated Data used to verify the data
        auth_tag (bytes): Authentication ntag to verify the data

    Returns:
        (bytes): Decrypted data
    """
    # Decrypt the JWE Ciphertext using the CEK, the JWE Initialization
    # Vector, the Additional Authenticated Data value, and the JWE
    # Authentication Tag (which is the Authentication Tag input to the
    # calculation) using the specified content encryption algorithm,
    # returning the decrypted plaintext
    # and validating the JWE
    # Authentication Tag in the manner specified for the algorithm,
    if enc in ALGORITHMS.HMAC_AUTH_TAG:
        encryption_key, mac_key, key_len = _get_encryption_key_mac_key_and_key_length_from_cek(cek_bytes, enc)
        auth_tag_check = _auth_tag(cipher_text, iv, aad, mac_key, key_len)

    # BCSC enc uses algorithm in ALGORITHMS.HMAC_AUTH_TAG, below will not run.
    elif enc in ALGORITHMS.GCM:
        encryption_key = bcsc_jwk.jwk_construct(cek_bytes, enc)
        auth_tag_check = auth_tag  # GCM check auth on decrypt
    else:
        raise NotImplementedError(f"enc {enc} is not implemented!")

    plaintext = encryption_key.decrypt(cipher_text, iv, aad, auth_tag)
    if auth_tag != auth_tag_check:
        raise JWEError("Invalid JWE Auth Tag")

    return plaintext


def _get_hmac_key(enc, mac_key_bytes):
    """
    Get an HMACKey for the provided encryption algorithm and key bytes

    Args:
        enc (str): Encryption algorithm
        mac_key_bytes (bytes): vytes for the HMAC key

    Returns:
         (HMACKey): The key to perform HMAC actions
    """
    _, hash_alg = enc.split("-")
    mac_key = bcsc_jwk.jwk_construct(mac_key_bytes, hash_alg)
    return mac_key


def _get_encryption_key_mac_key_and_key_length_from_cek(cek_bytes, enc):
    derived_key_len = len(cek_bytes) // 2
    mac_key_bytes = cek_bytes[0:derived_key_len]
    mac_key = _get_hmac_key(enc, mac_key_bytes)
    encryption_key_bytes = cek_bytes[-derived_key_len:]
    encryption_alg, _ = enc.split("-")
    encryption_key = bcsc_jwk.jwk_construct(encryption_key_bytes, encryption_alg)
    return encryption_key, mac_key, derived_key_len


def _jwe_compact_deserialize(jwe_bytes):
    """
    Deserialize and verify the header and segments are appropriate.

    Args:
        jwe_bytes (bytes): The compact serialized JWE
    Returns:
        (dict, bytes, bytes, bytes, bytes, bytes)
    """

    # Base64url decode the encoded representations of the JWE
    # Protected Header, the JWE Encrypted Key, the JWE Initialization
    # Vector, the JWE Ciphertext, the JWE Authentication Tag, and the
    # JWE AAD, following the restriction that no line breaks,
    # whitespace, or other additional characters have been used.
    jwe_bytes = utils.ensure_binary(jwe_bytes)
    try:
        header_segment, encrypted_key_segment, iv_segment, cipher_text_segment, auth_tag_segment = jwe_bytes.split(
            b".", 4
        )
        header_data = utils.base64url_decode(header_segment)
    except ValueError:
        raise JWEParseError("Not enough segments")
    except (TypeError):
        raise JWEParseError("Invalid header")

    # Verify that the octet sequence resulting from decoding the
    # encoded JWE Protected Header is a UTF-8-encoded representation
    # of a completely valid JSON object conforming to RFC 7159
    # [RFC7159]; let the JWE Protected Header be this JSON object.
    #
    # If using the JWE Compact Serialization, let the JOSE Header be
    # the JWE Protected Header.  Otherwise, when using the JWE JSON
    # Serialization, let the JOSE Header be the union of the members
    # of the JWE Protected Header, the JWE Shared Unprotected Header
    # and the corresponding JWE Per-Recipient Unprotected Header, all
    # of which must be completely valid JSON objects.  During this
    # step, verify that the resulting JOSE Header does not contain
    # duplicate Header Parameter names.  When using the JWE JSON
    # Serialization, this restriction includes that the same Header
    # Parameter name also MUST NOT occur in distinct JSON object
    # values that together comprise the JOSE Header.

    try:
        header = json.loads(header_data)
    except ValueError as e:
        raise JWEParseError(f"Invalid header string: {e}")

    if not isinstance(header, Mapping):
        raise JWEParseError("Invalid header string: must be a json object")

    try:
        encrypted_key = utils.base64url_decode(encrypted_key_segment)
    except (TypeError, binascii.Error):
        raise JWEParseError("Invalid encrypted key")

    try:
        iv = utils.base64url_decode(iv_segment)
    except (TypeError, binascii.Error):
        raise JWEParseError("Invalid IV")

    try:
        ciphertext = utils.base64url_decode(cipher_text_segment)
    except (TypeError, binascii.Error):
        raise JWEParseError("Invalid cyphertext")

    try:
        auth_tag = utils.base64url_decode(auth_tag_segment)
    except (TypeError, binascii.Error):
        raise JWEParseError("Invalid auth tag")

    return header, header_segment, encrypted_key, iv, ciphertext, auth_tag


def _big_endian(int_val):
    return pack("!Q", int_val)


def _auth_tag(ciphertext, iv, aad, mac_key, tag_length):
    """
    Get ann auth tag from the provided data

    Args:
        ciphertext (bytes): Encrypted value
        iv (bytes): Initialization vector
        aad (bytes): Additional Authenticated Data
        mac_key (bytes): Key to use in generating the MAC
        tag_length (int): How log the tag should be

    Returns:
        (bytes) Auth tag
    """
    al = _big_endian(len(aad) * 8)
    auth_tag_input = aad + iv + ciphertext + al
    signature = mac_key.sign(auth_tag_input)
    auth_tag = signature[0:tag_length]
    return auth_tag

