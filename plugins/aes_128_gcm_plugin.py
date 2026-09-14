"""AES-128-GCM encryption plugin for SF Encryptor."""

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from _authenticated_base import AuthenticatedPlugin


class EncryptorPlugin(AuthenticatedPlugin):
    name = "AES-128-GCM"
    description = "Authenticated AES encryption with a 128-bit key."
    key_length_bits = 128
    key_size = 16
    cipher_class = AESGCM