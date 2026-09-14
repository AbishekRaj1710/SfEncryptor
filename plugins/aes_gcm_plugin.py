"""AES-256-GCM encryption plugin for SF Encryptor."""

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from _authenticated_base import AuthenticatedPlugin


class EncryptorPlugin(AuthenticatedPlugin):
    name = "AES-256-GCM"
    description = "Authenticated AES encryption with a 256-bit key."
    key_length_bits = 256
    cipher_class = AESGCM
