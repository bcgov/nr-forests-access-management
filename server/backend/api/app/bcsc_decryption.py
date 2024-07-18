import binascii
import hashlib
import json
from collections.abc import Mapping
from struct import pack

from api.app.utils import utils
from jose import jwk


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
    # To get rid of using `python-jose` jwk library (not maintained),
    # comment below out as BCSC enc uses algorithm in ALGORITHMS.HMAC_AUTH_TAG
    elif enc in ALGORITHMS.GCM:
        encryption_key = _jwk_construct(cek_bytes, enc)
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
    mac_key = _jwk_construct(mac_key_bytes, hash_alg)
    return mac_key


def _get_encryption_key_mac_key_and_key_length_from_cek(cek_bytes, enc):
    derived_key_len = len(cek_bytes) // 2
    mac_key_bytes = cek_bytes[0:derived_key_len]
    mac_key = _get_hmac_key(enc, mac_key_bytes)
    encryption_key_bytes = cek_bytes[-derived_key_len:]
    encryption_alg, _ = enc.split("-")
    encryption_key = _jwk_construct(encryption_key_bytes, encryption_alg)
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
    jwe_bytes = ensure_binary(jwe_bytes)
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


def _jwk_construct(key_data, algorithm=None):
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


def ensure_binary(s):
    """Coerce **s** to bytes."""

    if isinstance(s, bytes):
        return s
    if isinstance(s, str):
        return s.encode("utf-8", "strict")
    raise TypeError(f"not expecting type '{type(s)}'")


class JWEError(Exception):
    """Base error for all JWE errors"""
    pass


class JWEParseError(JWEError):
    """Could not parse the JWE string provided"""
    pass


class JOSEError(Exception):
    pass


class JWKError(JOSEError):
    pass


class Algorithms:
    # DS Algorithms
    NONE = "none"
    HS256 = "HS256"
    HS384 = "HS384"
    HS512 = "HS512"
    RS256 = "RS256"
    RS384 = "RS384"
    RS512 = "RS512"
    ES256 = "ES256"
    ES384 = "ES384"
    ES512 = "ES512"

    # Content Encryption Algorithms
    A128CBC_HS256 = "A128CBC-HS256"
    A192CBC_HS384 = "A192CBC-HS384"
    A256CBC_HS512 = "A256CBC-HS512"
    A128GCM = "A128GCM"
    A192GCM = "A192GCM"
    A256GCM = "A256GCM"

    # Pseudo algorithm for encryption
    A128CBC = "A128CBC"
    A192CBC = "A192CBC"
    A256CBC = "A256CBC"

    # CEK Encryption Algorithms
    DIR = "dir"
    RSA1_5 = "RSA1_5"
    RSA_OAEP = "RSA-OAEP"
    RSA_OAEP_256 = "RSA-OAEP-256"
    A128KW = "A128KW"
    A192KW = "A192KW"
    A256KW = "A256KW"
    ECDH_ES = "ECDH-ES"
    ECDH_ES_A128KW = "ECDH-ES+A128KW"
    ECDH_ES_A192KW = "ECDH-ES+A192KW"
    ECDH_ES_A256KW = "ECDH-ES+A256KW"
    A128GCMKW = "A128GCMKW"
    A192GCMKW = "A192GCMKW"
    A256GCMKW = "A256GCMKW"
    PBES2_HS256_A128KW = "PBES2-HS256+A128KW"
    PBES2_HS384_A192KW = "PBES2-HS384+A192KW"
    PBES2_HS512_A256KW = "PBES2-HS512+A256KW"

    # Compression Algorithms
    DEF = "DEF"

    HMAC = {HS256, HS384, HS512}
    RSA_DS = {RS256, RS384, RS512}
    RSA_KW = {RSA1_5, RSA_OAEP, RSA_OAEP_256}
    RSA = RSA_DS.union(RSA_KW)
    EC_DS = {ES256, ES384, ES512}
    EC_KW = {ECDH_ES, ECDH_ES_A128KW, ECDH_ES_A192KW, ECDH_ES_A256KW}
    EC = EC_DS.union(EC_KW)
    AES_PSEUDO = {A128CBC, A192CBC, A256CBC, A128GCM, A192GCM, A256GCM}
    AES_JWE_ENC = {A128CBC_HS256, A192CBC_HS384, A256CBC_HS512, A128GCM, A192GCM, A256GCM}
    AES_ENC = AES_JWE_ENC.union(AES_PSEUDO)
    AES_KW = {A128KW, A192KW, A256KW}
    AEC_GCM_KW = {A128GCMKW, A192GCMKW, A256GCMKW}
    AES = AES_ENC.union(AES_KW)
    PBES2_KW = {PBES2_HS256_A128KW, PBES2_HS384_A192KW, PBES2_HS512_A256KW}

    HMAC_AUTH_TAG = {A128CBC_HS256, A192CBC_HS384, A256CBC_HS512}
    GCM = {A128GCM, A192GCM, A256GCM}

    SUPPORTED = HMAC.union(RSA_DS).union(EC_DS).union([DIR]).union(AES_JWE_ENC).union(RSA_KW).union(AES_KW)

    ALL = SUPPORTED.union([NONE]).union(AEC_GCM_KW).union(EC_KW).union(PBES2_KW)

    HASHES = {
        HS256: hashlib.sha256,
        HS384: hashlib.sha384,
        HS512: hashlib.sha512,
        RS256: hashlib.sha256,
        RS384: hashlib.sha384,
        RS512: hashlib.sha512,
        ES256: hashlib.sha256,
        ES384: hashlib.sha384,
        ES512: hashlib.sha512,
    }

    KEYS = {}


ALGORITHMS = Algorithms()
