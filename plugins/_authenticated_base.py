"""Shared helpers for built-in authenticated encryption plugins."""

import base64
import hashlib
import json
import os
import struct

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


MAGIC = b"SFE1"
SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32


class AuthenticatedPlugin:
    """Common file-envelope and key handling for AEAD plugins."""

    cipher_class = None
    name = ""
    description = ""
    key_length_bits = 256
    key_size = KEY_SIZE

    def _validate_key(self, key):
        if not isinstance(key, bytes) or len(key) != self.key_size:
            raise ValueError(
                f"Encryption keys must be exactly {self.key_size} bytes ({self.key_length_bits} bits)"
            )
        return key

    def _derive_key(self, password, salt, iterations):
        if not password:
            raise ValueError("A password is required")
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.key_size,
            salt=salt,
            iterations=iterations,
        )
        return kdf.derive(password.encode("utf-8"))

    def _load_key_file(self, key_file):
        with open(key_file, "rb") as handle:
            data = handle.read().strip()
        try:
            data = base64.b64decode(data, validate=True)
        except Exception:
            pass
        return self._validate_key(data)

    def _cipher(self, key):
        return self.cipher_class(self._validate_key(key))

    def encrypt(self, data, key):
        """Encrypt bytes and return (ciphertext, nonce)."""
        nonce = os.urandom(NONCE_SIZE)
        encrypted = self._cipher(key).encrypt(nonce, data, None)
        return encrypted, nonce

    def decrypt(self, encrypted_data, key, nonce_iv=None):
        """Decrypt bytes using the nonce supplied by the core engine."""
        if not nonce_iv:
            raise ValueError("A nonce is required for decryption")
        return self._cipher(key).decrypt(nonce_iv, encrypted_data, None)

    def generate_key(self):
        return os.urandom(self.key_size)

    def encrypt_file(self, input_filepath, output_filepath, key=None, password=None,
                     progress_callback=None, iterations=100000, compression="None",
                     integrity_check="None"):
        with open(input_filepath, "rb") as source:
            plaintext = source.read()

        salt = os.urandom(SALT_SIZE) if password else b""
        actual_key = self._derive_key(password, salt, iterations) if password else self._load_key_file(key)
        nonce = os.urandom(NONCE_SIZE)
        metadata = {
            "algorithm": self.name,
            "iterations": iterations if password else None,
            "password_based": bool(password),
        }
        header = json.dumps(metadata, separators=(",", ":")).encode("utf-8")
        ciphertext = self._cipher(actual_key).encrypt(nonce, plaintext, header)

        with open(output_filepath, "wb") as target:
            target.write(MAGIC)
            target.write(struct.pack(">H", len(header)))
            target.write(header)
            target.write(salt)
            target.write(nonce)
            target.write(ciphertext)

        if progress_callback:
            progress_callback(100)

    def decrypt_file(self, input_filepath, output_filepath, key=None, password=None,
                     progress_callback=None, iterations=100000, decompression="None",
                     integrity_check="None"):
        with open(input_filepath, "rb") as source:
            payload = source.read()

        if not payload.startswith(MAGIC):
            raise ValueError("Unsupported encrypted file format")
        header_size = struct.unpack(">H", payload[4:6])[0]
        header_start = 6
        header_end = header_start + header_size
        header_bytes = payload[header_start:header_end]
        metadata = json.loads(header_bytes.decode("utf-8"))
        cursor = header_end
        salt = payload[cursor:cursor + SALT_SIZE] if metadata["password_based"] else b""
        cursor += SALT_SIZE if metadata["password_based"] else 0
        nonce = payload[cursor:cursor + NONCE_SIZE]
        ciphertext = payload[cursor + NONCE_SIZE:]

        if metadata["password_based"]:
            actual_key = self._derive_key(password, salt, metadata["iterations"])
        else:
            actual_key = self._load_key_file(key)
        plaintext = self._cipher(actual_key).decrypt(nonce, ciphertext, header_bytes)

        with open(output_filepath, "wb") as target:
            target.write(plaintext)
        if progress_callback:
            progress_callback(100)
