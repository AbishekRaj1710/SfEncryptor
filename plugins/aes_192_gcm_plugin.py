"""AES-192-GCM encryption plugin for SF Encryptor."""

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from _authenticated_base import AuthenticatedPlugin


class EncryptorPlugin(AuthenticatedPlugin):
    name = "AES-192-GCM"
    description = "Authenticated AES encryption with a 192-bit key."
    key_length_bits = 192
    key_size = 24
    cipher_class = AESGCM