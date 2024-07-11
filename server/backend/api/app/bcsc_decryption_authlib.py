import logging

from authlib.common.encoding import to_bytes
from authlib.jose.errors import (DecodeError, InvalidHeaderParameterNameError,
                                 MissingAlgorithmError,
                                 MissingEncryptionAlgorithmError,
                                 UnsupportedAlgorithmError,
                                 UnsupportedCompressionAlgorithmError,
                                 UnsupportedEncryptionAlgorithmError)
from authlib.jose.rfc7516.models import JWEAlgorithmWithTagAwareKeyAgreement
from authlib.jose.rfc7518.jwe_algs import JWE_ALG_ALGORITHMS, RSAAlgorithm
from authlib.jose.rfc7518.jwe_encs import (JWE_ENC_ALGORITHMS,
                                           CBCHS2EncAlgorithm)
from authlib.jose.util import extract_header, extract_segment
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

LOGGER = logging.getLogger(__name__)


def register_bcsc_jwe_rfc7518():
    # 'alg'
    JsonWebEncryption.register_algorithm(RSAAlgorithm(
            'RSA-OAEP-256', 'RSAES OAEP using SHA-256 and MGF1 with SHA-256',
            padding.OAEP(padding.MGF1(hashes.SHA256()), hashes.SHA256(), None)
    ))
    # 'enc'
    JsonWebEncryption.register_algorithm(CBCHS2EncAlgorithm(256, 512))


class JsonWebEncryption:
    #: Registered Header Parameter Names defined by Section 4.1
    REGISTERED_HEADER_PARAMETER_NAMES = frozenset([
        'alg', 'enc', 'zip',
        'jku', 'jwk', 'kid',
        'x5u', 'x5c', 'x5t', 'x5t#S256',
        'typ', 'cty', 'crit'
    ])

    ALG_REGISTRY = {}
    # ALG_REGISTRY = JWE_ALG_ALGORITHMS
    ENC_REGISTRY = {}
    # ENC_REGISTRY = JWE_ENC_ALGORITHMS
    ZIP_REGISTRY = {}

    def __init__(self, algorithms=None, private_headers=None):
        self._algorithms = algorithms
        self._private_headers = private_headers

    @classmethod
    def register_algorithm(cls, algorithm):
        """Register an algorithm for ``alg`` or ``enc`` or ``zip`` of JWE."""
        if not algorithm or algorithm.algorithm_type != 'JWE':
            raise ValueError(
                f'Invalid algorithm for JWE, {algorithm!r}')

        if algorithm.algorithm_location == 'alg':
            cls.ALG_REGISTRY[algorithm.name] = algorithm
        elif algorithm.algorithm_location == 'enc':
            cls.ENC_REGISTRY[algorithm.name] = algorithm
        elif algorithm.algorithm_location == 'zip':
            cls.ZIP_REGISTRY[algorithm.name] = algorithm

    def deserialize_compact(self, s, key, decode=None, sender_key=None):
        """Extract JWE Compact Serialization.

        :param s: JWE Compact Serialization as bytes
        :param key: Private key used to decrypt payload
            (optionally can be a tuple of kid and essentially key)
        :param decode: Function to decode payload data
        :param sender_key: Sender's public key in case
            JWEAlgorithmWithTagAwareKeyAgreement is used
        :return: dict with `header` and `payload` keys where `header` value is
            a dict containing protected header fields
        """
        try:
            s = to_bytes(s)
            protected_s, ek_s, iv_s, ciphertext_s, tag_s = s.rsplit(b'.')
            LOGGER.info(
                "bcsc_decryption_authlib:deserialize_compact:rsplit:"
                f"protected_s - {protected_s},"
                f"ek_s - {ek_s},"
                f"iv_s - {iv_s},"
                f"ciphertext_s - {ciphertext_s},"
                f"tag_s - {tag_s},"
            )
        except ValueError:
            raise DecodeError('Not enough segments')

        protected = extract_header(protected_s, DecodeError)
        LOGGER.info(
            "bcsc_decryption_authlib:deserialize_compact"
            f"extract_header - {protected},"
        )
        ek = extract_segment(ek_s, DecodeError, 'encryption key')
        iv = extract_segment(iv_s, DecodeError, 'initialization vector')
        ciphertext = extract_segment(ciphertext_s, DecodeError, 'ciphertext')
        tag = extract_segment(tag_s, DecodeError, 'authentication tag')

        LOGGER.info(
            "bcsc_decryption_authlib:deserialize_compact:extract_segment"
            f"protected - {protected},"
            f"ek - {ek},"
            f"iv - {iv},"
            f"ciphertext - {ciphertext},"
            f"tag - {tag},"
        )

        alg = self.get_header_alg(protected)
        enc = self.get_header_enc(protected)
        zip_alg = self.get_header_zip(protected)

        LOGGER.info(
            "bcsc_decryption_authlib:deserialize_compact:extract_segment"
            f"alg - {alg},"
            f"enc - {enc},"
            f"zip_alg - {zip_alg},"
        )

        self._validate_sender_key(sender_key, alg)
        self._validate_private_headers(protected, alg)

        if isinstance(key, tuple) and len(key) == 2:
            LOGGER.info(
                "bcsc_decryption_authlib:deserialize_compact - len(key) == 2 "
            )
            # Ignore separately provided kid, extract essentially key only
            key = key[1]

        key = prepare_key(alg, protected, key)

        if sender_key is not None:
            sender_key = alg.prepare_key(sender_key)
            LOGGER.info(
                f"bcsc_decryption_authlib:deserialize_compact - \
                sender_key {sender_key} "
            )

        if isinstance(alg, JWEAlgorithmWithTagAwareKeyAgreement):
            # For a JWE algorithm with tag-aware key agreement:
            if alg.key_size is not None:
                LOGGER.info(
                    "bcsc_decryption_authlib:deserialize_compact - \
                    alg.key_size is not None "
                )
                # In case key agreement with key wrapping mode is used:
                # Provide authentication tag to .unwrap method
                cek = alg.unwrap(enc, ek, protected, key, sender_key, tag)
            else:
                # Otherwise, don't provide authentication tag to .unwrap method
                cek = alg.unwrap(enc, ek, protected, key, sender_key)
        else:
            LOGGER.info(
                "bcsc_decryption_authlib:deserialize_compact - \
                not isInstance JWEAlgorithmWithTagAwareKeyAgreement"
            )
            # For any other JWE algorithm:
            # Don't provide authentication tag to .unwrap method
            cek = alg.unwrap(enc, ek, protected, key)
            LOGGER.info(
                "bcsc_decryption_authlib:deserialize_compact - cek:{cek} "
            )

        aad = to_bytes(protected_s, 'ascii')
        msg = enc.decrypt(ciphertext, aad, iv, tag, cek)

        if zip_alg:
            payload = zip_alg.decompress(to_bytes(msg))
        else:
            payload = msg

        if decode:
            payload = decode(payload)
        return {'header': protected, 'payload': payload}

    def deserialize(self, obj, key, decode=None, sender_key=None):
        """Extract a JWE Serialization.

        It supports both compact and JSON serialization.

        :param obj: JWE compact serialization as bytes or
            JWE JSON serialization as dict or str
        :param key: Private key used to decrypt payload
            (optionally can be a tuple of kid and essentially key)
        :param decode: Function to decode payload data
        :param sender_key: Sender's public key in case
            JWEAlgorithmWithTagAwareKeyAgreement is used
        :return: dict with `header` and `payload` keys
        """
        if isinstance(obj, dict):
            return self.deserialize_json(obj, key, decode, sender_key)

        obj = to_bytes(obj)
        if obj.startswith(b'{') and obj.endswith(b'}'):
            return self.deserialize_json(obj, key, decode, sender_key)

        return self.deserialize_compact(obj, key, decode, sender_key)

    def get_header_alg(self, header):
        if 'alg' not in header:
            raise MissingAlgorithmError()

        alg = header['alg']
        LOGGER.info(
            "bcsc_decryption_authlib:get_header_alg -"
            f"header['alg']: {alg}"
        )
        if self._algorithms is not None and alg not in self._algorithms:
            raise UnsupportedAlgorithmError()
        if alg not in self.ALG_REGISTRY:
            LOGGER.info("raise error due to 'alg' not in self.ALG_REGISTRY")
            raise UnsupportedAlgorithmError()
        return self.ALG_REGISTRY[alg]

    def get_header_enc(self, header):
        if 'enc' not in header:
            raise MissingEncryptionAlgorithmError()
        enc = header['enc']
        if self._algorithms is not None and enc not in self._algorithms:
            raise UnsupportedEncryptionAlgorithmError()
        if enc not in self.ENC_REGISTRY:
            LOGGER.info("raise error due to 'enc' not in self.ENC_REGISTRY")
            raise UnsupportedEncryptionAlgorithmError()
        return self.ENC_REGISTRY[enc]

    def get_header_zip(self, header):
        if 'zip' in header:
            z = header['zip']
            if self._algorithms is not None and z not in self._algorithms:
                raise UnsupportedCompressionAlgorithmError()
            if z not in self.ZIP_REGISTRY:
                raise UnsupportedCompressionAlgorithmError()
            return self.ZIP_REGISTRY[z]

    def _validate_sender_key(self, sender_key, alg):
        if isinstance(alg, JWEAlgorithmWithTagAwareKeyAgreement):
            if sender_key is None:
                raise ValueError("{} algorithm requires sender_key but passed sender_key value is None"
                                 .format(alg.name))
        else:
            if sender_key is not None:
                raise ValueError("{} algorithm does not use sender_key but passed sender_key value is not None"
                                 .format(alg.name))

    def _validate_private_headers(self, header, alg):
        # only validate private headers when developers set
        # private headers explicitly
        if self._private_headers is None:
            return

        names = self.REGISTERED_HEADER_PARAMETER_NAMES.copy()
        names = names.union(self._private_headers)

        if alg.EXTRA_HEADERS:
            names = names.union(alg.EXTRA_HEADERS)

        for k in header:
            if k not in names:
                raise InvalidHeaderParameterNameError(k)


def prepare_key(alg, header, key):
    LOGGER.info(
        "bcsc_decryption_authlib:prepare_key: "
        f"alg: {alg}, "
        f"header: {header}, "
        f"key: {key}"
    )
    if callable(key):
        LOGGER.info(
            f"callable:key: {key}"
        )
        key = key(header, None)
    elif key is None and 'jwk' in header:
        LOGGER.info(
            f"key is None and header['jwk']: {key}"
        )
        key = header['jwk']
    prepared_key = alg.prepare_key(key)
    LOGGER.info(
        f"prepared_key: {prepared_key}"
    )
    return prepared_key
