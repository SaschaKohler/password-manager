"""
Core encryption utilities for password manager.

Provides secure encryption and decryption functions using AES-256-GCM
with proper key derivation and random nonce generation.
"""

import os
import hashlib
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from typing import Tuple, Optional, Union
import base64
import json

from .exceptions import EncryptionError, DecryptionError


class PasswordEncryption:
    """Handles password encryption and decryption with AES-256-GCM."""
    
    def __init__(self, master_key: bytes) -> None:
        """
        Initialize encryption with master key.
        
        Args:
            master_key: 32-byte master encryption key
        """
        if len(master_key) != 32:
            raise EncryptionError("Master key must be 32 bytes")
        
        self.master_key = master_key
        self.backend = default_backend()
    
    @classmethod
    def derive_key_from_password(cls, password: str, salt: bytes, iterations: int = 100000) -> bytes:
        """
        Derive encryption key from password using PBKDF2.
        
        Args:
            password: User's master password
            salt: Random salt (16 bytes recommended)
            iterations: Number of PBKDF2 iterations
            
        Returns:
            32-byte derived key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=iterations,
            backend=default_backend()
        )
        return kdf.derive(password.encode('utf-8'))
    
    @classmethod
    def generate_salt(cls) -> bytes:
        """Generate cryptographically secure salt."""
        return os.urandom(16)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext using AES-256-GCM.
        
        Args:
            plaintext: Data to encrypt
            
        Returns:
            Base64-encoded encrypted data (nonce + ciphertext + tag)
            
        Raises:
            EncryptionError: If encryption fails
        """
        try:
            # Generate random nonce (12 bytes for GCM)
            nonce = os.urandom(12)
            
            # Initialize AES-GCM cipher
            aesgcm = AESGCM(self.master_key)
            
            # Encrypt data
            ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
            
            # Combine nonce and ciphertext
            encrypted_data = nonce + ciphertext
            
            # Return base64-encoded result
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            raise EncryptionError(f"Encryption failed: {str(e)}")
    
    def decrypt(self, encrypted_b64: str) -> str:
        """
        Decrypt base64-encoded encrypted data.
        
        Args:
            encrypted_b64: Base64-encoded encrypted data
            
        Returns:
            Decrypted plaintext
            
        Raises:
            DecryptionError: If decryption fails
        """
        try:
            # Decode base64
            encrypted_data = base64.b64decode(encrypted_b64.encode('utf-8'))
            
            # Extract nonce (first 12 bytes)
            nonce = encrypted_data[:12]
            ciphertext = encrypted_data[12:]
            
            # Initialize AES-GCM cipher
            aesgcm = AESGCM(self.master_key)
            
            # Decrypt data
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            
            return plaintext.decode('utf-8')
            
        except Exception as e:
            raise DecryptionError(f"Decryption failed: {str(e)}")
    
    def encrypt_password_entry(self, title: str, username: str, password: str,
                              url: Optional[str] = None, notes: Optional[str] = None,
                              username2: Optional[str] = None, username3: Optional[str] = None,
                              otp_url: Optional[str] = None, custom_fields: Optional[dict] = None) -> str:
        """
        Encrypt a complete password entry.

        Args:
            title: Entry title
            username: Username/email
            password: Password
            url: Optional URL
            notes: Optional notes
            username2: Optional secondary username
            username3: Optional tertiary username
            otp_url: Optional OTP/TOTP URL
            custom_fields: Optional dictionary for custom fields from other password managers

        Returns:
            Base64-encoded encrypted entry
        """
        entry_data = {
            'title': title,
            'username': username,
            'password': password,
            'url': url,
            'notes': notes,
            'username2': username2,
            'username3': username3,
            'otp_url': otp_url,
            'custom_fields': custom_fields or {},
            'created_at': secrets.token_hex(16)  # Unique identifier
        }

        json_data = json.dumps(entry_data, separators=(',', ':'))
        return self.encrypt(json_data)
    
    def decrypt_password_entry(self, encrypted_entry: str) -> dict:
        """
        Decrypt a complete password entry.
        
        Args:
            encrypted_entry: Base64-encoded encrypted entry
            
        Returns:
            Decrypted entry as dictionary
        """
        json_data = self.decrypt(encrypted_entry)
        return json.loads(json_data)


class KeyManager:
    """Manages encryption keys and key rotation."""
    
    def __init__(self, user_id: int) -> None:
        """Initialize key manager for user."""
        self.user_id = user_id
    
    def generate_master_key(self) -> bytes:
        """Generate a new master encryption key."""
        return os.urandom(32)
    
    def encrypt_master_key(self, master_key: bytes, password: str, salt: bytes) -> str:
        """
        Encrypt master key with user's password.
        
        Args:
            master_key: Master key to encrypt
            password: User's password
            salt: Salt for key derivation
            
        Returns:
            Base64-encoded encrypted master key
        """
        # Derive key from password
        derived_key = PasswordEncryption.derive_key_from_password(password, salt)
        
        # Encrypt master key with derived key
        encryptor = PasswordEncryption(derived_key)
        return encryptor.encrypt(master_key.hex())
    
    def decrypt_master_key(self, encrypted_key: str, password: str, salt: bytes) -> bytes:
        """
        Decrypt master key with user's password.
        
        Args:
            encrypted_key: Base64-encoded encrypted master key
            password: User's password
            salt: Salt for key derivation
            
        Returns:
            Decrypted master key
        """
        # Derive key from password
        derived_key = PasswordEncryption.derive_key_from_password(password, salt)
        
        # Decrypt master key
        decryptor = PasswordEncryption(derived_key)
        master_key_hex = decryptor.decrypt(encrypted_key)
        
        return bytes.fromhex(master_key_hex)


class PasswordGenerator:
    """Generates secure random passwords."""
    
    LOWERCASE = 'abcdefghijklmnopqrstuvwxyz'
    UPPERCASE = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    DIGITS = '0123456789'
    SYMBOLS = '!@#$%^&*()_+-=[]{}|;:,.<>?'
    
    @classmethod
    def generate(cls, length: int = 16, use_symbols: bool = True, 
                 use_lowercase: bool = True, use_uppercase: bool = True, 
                 use_digits: bool = True) -> str:
        """
        Generate a secure random password.
        
        Args:
            length: Password length
            use_symbols: Include symbols
            use_lowercase: Include lowercase letters
            use_uppercase: Include uppercase letters
            use_digits: Include digits
            
        Returns:
            Generated password
        """
        if length < 8:
            raise ValueError("Password length must be at least 8 characters")
        
        # Build character set
        charset = ''
        if use_lowercase:
            charset += cls.LOWERCASE
        if use_uppercase:
            charset += cls.UPPERCASE
        if use_digits:
            charset += cls.DIGITS
        if use_symbols:
            charset += cls.SYMBOLS
        
        if not charset:
            raise ValueError("At least one character type must be selected")
        
        # Generate password
        password = ''.join(secrets.choice(charset) for _ in range(length))
        
        # Ensure password contains at least one character from each selected type
        if use_lowercase and not any(c in cls.LOWERCASE for c in password):
            password = cls.LOWERCASE[0] + password[:-1]
        if use_uppercase and not any(c in cls.UPPERCASE for c in password):
            password = cls.UPPERCASE[0] + password[:-1]
        if use_digits and not any(c in cls.DIGITS for c in password):
            password = cls.DIGITS[0] + password[:-1]
        if use_symbols and not any(c in cls.SYMBOLS for c in password):
            password = cls.SYMBOLS[0] + password[:-1]
        
        return password
    
    @classmethod
    def generate_passphrase(cls, word_count: int = 4, separator: str = '-', 
                           capitalize: bool = True) -> str:
        """
        Generate a memorable passphrase.
        
        Args:
            word_count: Number of words
            separator: Word separator
            capitalize: Capitalize first letter of each word
            
        Returns:
            Generated passphrase
        """
        # Simple word list for demonstration
        words = [
            'apple', 'banana', 'coffee', 'dragon', 'elephant', 'forest',
            'guitar', 'house', 'island', 'jungle', 'kitten', 'lemon',
            'mountain', 'nature', 'ocean', 'piano', 'queen', 'river',
            'sunset', 'tiger', 'umbrella', 'valley', 'window', 'yellow'
        ]
        
        selected_words = [secrets.choice(words) for _ in range(word_count)]
        
        if capitalize:
            selected_words = [word.capitalize() for word in selected_words]
        
        return separator.join(selected_words)


def validate_password_strength(password: str) -> dict:
    """
    Validate password strength and return feedback.
    
    Args:
        password: Password to validate
        
    Returns:
        Dictionary with strength score and feedback
    """
    feedback = []
    score = 0
    
    # Length check
    if len(password) >= 12:
        score += 2
    elif len(password) >= 8:
        score += 1
    else:
        feedback.append("Password should be at least 8 characters long")
    
    # Character variety
    if any(c.islower() for c in password):
        score += 1
    else:
        feedback.append("Include lowercase letters")
    
    if any(c.isupper() for c in password):
        score += 1
    else:
        feedback.append("Include uppercase letters")
    
    if any(c.isdigit() for c in password):
        score += 1
    else:
        feedback.append("Include numbers")
    
    if any(c in PasswordGenerator.SYMBOLS for c in password):
        score += 1
    else:
        feedback.append("Include symbols")
    
    # Common patterns
    if password.lower() in ['password', '123456', 'qwerty', 'admin']:
        score = 0
        feedback.append("Avoid common passwords")
    
    strength_levels = {
        0: 'Very Weak',
        1: 'Weak',
        2: 'Fair',
        3: 'Good',
        4: 'Strong',
        5: 'Very Strong',
        6: 'Excellent'
    }
    
    return {
        'score': score,
        'strength': strength_levels.get(score, 'Unknown'),
        'feedback': feedback
    }
