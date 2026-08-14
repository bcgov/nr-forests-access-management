"""
Characterization tests for BCSC JWE decryption.

These pin down the behaviour of the ported `python-jose` code in
`api/app/integration/bcsc/` that sits directly on top of the `cryptography`
package (AES-CBC `Cipher`, `PKCS7` padding, `InvalidTag`). They exist so that
a `cryptography` version bump is verified against real decryption behaviour
rather than an import check.

Two independent guards are used:

1. FROZEN_VECTORS - JWE strings generated once against cryptography 48.0.1 and
   hardcoded here. If a future `cryptography` release changes AES-CBC or PKCS7
   behaviour, these stop decrypting to the known plaintext.
2. `build_jwe()` - re-encrypts at test time using `cryptography` primitives
   directly, so the test acts as an oracle independent of the module under test.

The tests are pure: no database, no network, no environment variables and no
patching of global state. They therefore need no marker or monkeypatch and
cannot leak into any other test.
"""

import base64
import hashlib
import hmac
import json
import logging
from struct import pack

import pytest
from api.app.integration.bcsc import bcsc_decryption
from api.app.integration.bcsc.bcsc_constants import (JWEError, JWEParseError)
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7

LOGGER = logging.getLogger(__name__)

# CEK byte length and HMAC hash for each AES-CBC-HMAC content encryption
# algorithm, per RFC 7518 section 5.2.
CBC_HMAC_SPECS = {
    "A128CBC-HS256": (32, hashlib.sha256),
    "A192CBC-HS384": (48, hashlib.sha384),
    "A256CBC-HS512": (64, hashlib.sha512),
}

PLAIN_TEXT = b'{"sub":"test-bcsc-subject","given_name":"Ada"}'

# Generated once against cryptography 48.0.1; see module docstring.
# (base64 standard-encoded CEK, compact JWE string)
FROZEN_VECTORS = {
    "A128CBC-HS256": (
        "AwoRGB8mLTQ7QklQV15lbHN6gYiPlp2kq7K5wMfO1dw=",
        "eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0.."
        "BRAbJjE8R1JdaHN-iZSfqg."
        "gU540Ig6DDtLNmXlLUrLFlE90feDLRyRSbalBZBWs9Ok8b1Huh8H-GVWDcMq1VUE."
        "qUhEXhQCFPWFuK1yfnjmhg",
    ),
    "A192CBC-HS384": (
        "AwoRGB8mLTQ7QklQV15lbHN6gYiPlp2kq7K5wMfO1dzj6vH4/wYNFBsiKTA3PkVM",
        "eyJhbGciOiJkaXIiLCJlbmMiOiJBMTkyQ0JDLUhTMzg0In0.."
        "BRAbJjE8R1JdaHN-iZSfqg."
        "gm-NB524sbvjE50vfniPp25tIRw5cPxq-CzEDzIMUrHJdNKozuGRoxcMU2Fpm0pk."
        "I8Ldy86YmVOOCiqorC5fseNqLCLhEJi-",
    ),
    "A256CBC-HS512": (
        "AwoRGB8mLTQ7QklQV15lbHN6gYiPlp2kq7K5wMfO1dzj6vH4/wYNFBsiKTA3PkVM"
        "U1phaG92fYSLkpmgp661vA==",
        "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2Q0JDLUhTNTEyIn0.."
        "BRAbJjE8R1JdaHN-iZSfqg."
        "z9suEvFU6eZGE1_R4Ct5djHUPln4PIFzPn8Qi8ZvAMSHyy55Q98mktthsBruKMwf."
        "FWQtHzBVKDIwOq2BFSrN97HKD2k027F5Gq_03PSXNPY",
    ),
}


def b64u(raw: bytes) -> bytes:
    """base64url encode without padding, matching JWE compact serialization."""
    return base64.urlsafe_b64encode(raw).replace(b"=", b"")


def build_jwe(enc="A128CBC-HS256", plain_text=PLAIN_TEXT, alg="dir", header=None):
    """
    Build a valid compact JWE for an AES-CBC-HMAC algorithm.

    Encryption is done here with `cryptography` primitives directly so this
    helper stays independent of the module under test.

    Returns:
        (bytes, bytes): the CEK and the compact serialized JWE.
    """
    cek_len, hash_alg = CBC_HMAC_SPECS[enc]
    cek = bytes((i * 7 + 3) % 256 for i in range(cek_len))
    iv = bytes((i * 11 + 5) % 256 for i in range(16))
    half = cek_len // 2
    mac_key, enc_key = cek[:half], cek[half:]

    if header is None:
        header = {"alg": alg, "enc": enc}
    header_segment = b64u(json.dumps(header, separators=(",", ":")).encode())

    padder = PKCS7(algorithms.AES.block_size).padder()
    padded = padder.update(plain_text) + padder.finalize()
    encryptor = Cipher(
        algorithms.AES(enc_key), modes.CBC(iv), backend=default_backend()
    ).encryptor()
    cipher_text = encryptor.update(padded) + encryptor.finalize()

    # RFC 7518 section 5.2.2.1: tag is HMAC over AAD || IV || ciphertext || AL,
    # truncated to half the CEK length.
    aad = header_segment
    al = pack("!Q", len(aad) * 8)
    auth_tag = hmac.new(mac_key, aad + iv + cipher_text + al, hash_alg).digest()[:half]

    jwe = b".".join([header_segment, b"", b64u(iv), b64u(cipher_text), b64u(auth_tag)])
    return cek, jwe


def flip_last_byte(segment_b64: bytes) -> bytes:
    """Flip one bit in the last byte of a base64url segment's decoded value."""
    raw = bytearray(base64.urlsafe_b64decode(segment_b64 + b"=" * (-len(segment_b64) % 4)))
    raw[-1] ^= 0x01
    return b64u(bytes(raw))


class TestDecryptHappyPath:

    @pytest.mark.parametrize("enc", list(FROZEN_VECTORS))
    def test_frozen_vector_decrypts_to_known_plaintext(self, enc):
        """Guards against silent behaviour changes in AES-CBC / PKCS7."""
        cek_b64, jwe = FROZEN_VECTORS[enc]
        cek = base64.b64decode(cek_b64)

        assert bcsc_decryption.decrypt(jwe, cek) == PLAIN_TEXT

    @pytest.mark.parametrize("enc", list(CBC_HMAC_SPECS))
    def test_decrypt_round_trip(self, enc):
        cek, jwe = build_jwe(enc=enc)

        assert bcsc_decryption.decrypt(jwe, cek) == PLAIN_TEXT

    def test_decrypt_accepts_str_and_bytes(self):
        cek, jwe = build_jwe()

        assert bcsc_decryption.decrypt(jwe, cek) == PLAIN_TEXT
        assert bcsc_decryption.decrypt(jwe.decode(), cek) == PLAIN_TEXT

    @pytest.mark.parametrize(
        "length",
        # Around the AES 16-byte block boundary, where PKCS7 padding is
        # most likely to break: empty, sub-block, exact block, block + 1.
        [0, 1, 15, 16, 17, 31, 32, 33],
    )
    def test_decrypt_handles_pkcs7_padding_boundaries(self, length):
        plain_text = b"x" * length
        cek, jwe = build_jwe(plain_text=plain_text)

        assert bcsc_decryption.decrypt(jwe, cek) == plain_text

    def test_get_unverified_header_returns_header(self):
        _cek, jwe = build_jwe(enc="A256CBC-HS512")

        assert bcsc_decryption.get_unverified_header(jwe) == {
            "alg": "dir",
            "enc": "A256CBC-HS512",
        }

    def test_get_unverified_header_does_not_verify_auth_tag(self):
        """Header parsing must work even when the token would fail decryption."""
        _cek, jwe = build_jwe()
        parts = jwe.split(b".")
        tampered = b".".join(parts[:4] + [flip_last_byte(parts[4])])

        assert bcsc_decryption.get_unverified_header(tampered) == {
            "alg": "dir",
            "enc": "A128CBC-HS256",
        }


class TestDecryptRejectsTamperedToken:
    """The security-relevant half: these must keep failing after a bump."""

    def test_tampered_auth_tag_is_rejected(self):
        cek, jwe = build_jwe()
        parts = jwe.split(b".")
        tampered = b".".join(parts[:4] + [flip_last_byte(parts[4])])

        with pytest.raises(JWEError):
            bcsc_decryption.decrypt(tampered, cek)

    def test_tampered_cipher_text_is_rejected(self):
        cek, jwe = build_jwe()
        parts = jwe.split(b".")
        tampered = b".".join(parts[:3] + [flip_last_byte(parts[3]), parts[4]])

        with pytest.raises(JWEError):
            bcsc_decryption.decrypt(tampered, cek)

    def test_tampered_iv_is_rejected(self):
        cek, jwe = build_jwe()
        parts = jwe.split(b".")
        tampered = b".".join(parts[:2] + [flip_last_byte(parts[2])] + parts[3:])

        with pytest.raises(JWEError):
            bcsc_decryption.decrypt(tampered, cek)

    def test_tampered_protected_header_is_rejected(self):
        """The protected header is the AAD, so re-ordering its keys breaks the tag."""
        cek, jwe = build_jwe()
        parts = jwe.split(b".")
        # Same alg/enc, different encoded bytes.
        reordered = b64u(
            json.dumps({"enc": "A128CBC-HS256", "alg": "dir"}, separators=(",", ":")).encode()
        )
        tampered = b".".join([reordered] + parts[1:])

        with pytest.raises(JWEError):
            bcsc_decryption.decrypt(tampered, cek)

    def test_wrong_cek_is_rejected(self):
        _cek, jwe = build_jwe()
        wrong_cek = bytes(32)

        with pytest.raises(JWEError):
            bcsc_decryption.decrypt(jwe, wrong_cek)


class TestDecryptRejectsMalformedToken:

    @pytest.mark.parametrize(
        "header",
        [
            {"alg": "dir", "enc": "NOT-AN-ALGORITHM"},
            {"alg": "NOT-AN-ALGORITHM", "enc": "A128CBC-HS256"},
        ],
    )
    def test_unsupported_algorithm_is_rejected(self, header):
        cek, jwe = build_jwe(header=header)

        with pytest.raises(JWEError, match="not supported"):
            bcsc_decryption.decrypt(jwe, cek)

    @pytest.mark.parametrize(
        "header", [{"alg": "dir"}, {"enc": "A128CBC-HS256"}, {}]
    )
    def test_missing_alg_or_enc_is_rejected(self, header):
        cek, jwe = build_jwe(header=header)

        with pytest.raises(JWEParseError, match="alg and enc headers are required"):
            bcsc_decryption.decrypt(jwe, cek)

    def test_too_few_segments_is_rejected(self):
        with pytest.raises(JWEParseError, match="Not enough segments"):
            bcsc_decryption.decrypt(b"only.three.segments", bytes(32))

    def test_non_json_header_is_rejected(self):
        jwe = b".".join([b64u(b"not json at all"), b"", b"", b"", b""])

        with pytest.raises(JWEParseError, match="Invalid header string"):
            bcsc_decryption.decrypt(jwe, bytes(32))

    def test_non_object_header_is_rejected(self):
        jwe = b".".join([b64u(b"[1, 2, 3]"), b"", b"", b"", b""])

        with pytest.raises(JWEParseError, match="must be a json object"):
            bcsc_decryption.decrypt(jwe, bytes(32))


class TestKeyDerivation:
    """RFC 7518 section 5.2.2.1 CEK split - pinned so a refactor can't invert it."""

    @pytest.mark.parametrize(
        "enc, expected_half", [("A128CBC-HS256", 16), ("A192CBC-HS384", 24), ("A256CBC-HS512", 32)]
    )
    def test_cek_splits_into_mac_key_then_encryption_key(self, enc, expected_half):
        cek_len, _hash_alg = CBC_HMAC_SPECS[enc]
        cek = bytes(range(cek_len))

        (
            encryption_key,
            mac_key,
            key_len,
        ) = bcsc_decryption._get_encryption_key_mac_key_and_key_length_from_cek(cek, enc)

        assert key_len == expected_half
        # MAC key is the leading half, encryption key the trailing half.
        assert mac_key.prepared_key == cek[:expected_half]
        assert encryption_key._key == cek[expected_half:]

    def test_auth_tag_matches_rfc_7518_construction(self):
        """Independently recompute the tag with stdlib hmac."""
        enc = "A128CBC-HS256"
        cek = bytes((i * 7 + 3) % 256 for i in range(32))
        iv = bytes(range(16))
        aad = b"eyJhbGciOiJkaXIifQ"
        cipher_text = b"some-cipher-text"

        _enc_key, mac_key, key_len = (
            bcsc_decryption._get_encryption_key_mac_key_and_key_length_from_cek(cek, enc)
        )
        actual = bcsc_decryption._auth_tag(cipher_text, iv, aad, mac_key, key_len)

        al = pack("!Q", len(aad) * 8)
        expected = hmac.new(
            cek[:16], aad + iv + cipher_text + al, hashlib.sha256
        ).digest()[:16]

        assert actual == expected
        assert len(actual) == 16
