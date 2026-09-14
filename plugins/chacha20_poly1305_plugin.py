"""ChaCha20-Poly1305 encryption plugin for SF Encryptor."""

from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

from _authenticated_base import AuthenticatedPlugin


class EncryptorPlugin(AuthenticatedPlugin):
    name = "ChaCha20-Poly1305"
    description = "Authenticated ChaCha20 encryption with a 256-bit key."
    key_length_bits = 256
    cipher_class = ChaCha20Poly1305
