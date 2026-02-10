"""
Custom exceptions for crypto operations.

Provides specific exception types for encryption, decryption,
and key management operations.
"""


class CryptoError(Exception):
    """Base exception for crypto operations."""
    pass


class EncryptionError(CryptoError):
    """Raised when encryption operation fails."""
    pass


class DecryptionError(CryptoError):
    """Raised when decryption operation fails."""
    pass


class KeyDerivationError(CryptoError):
    """Raised when key derivation fails."""
    pass


class InvalidKeyError(CryptoError):
    """Raised when provided key is invalid."""
    pass


class PasswordGenerationError(CryptoError):
    """Raised when password generation fails."""
    pass


class SecurityError(CryptoError):
    """Raised for general security-related errors."""
    pass
