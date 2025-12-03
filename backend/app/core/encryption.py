"""
Field-Level Encryption Module

This module provides encryption utilities for sensitive data including:
- AES-256-GCM encryption for field-level encryption
- Data masking for PII display
- Key derivation and management
- Encrypted field utilities
- Integration with environment-based key management

Author: BARQ Security Team
Last Updated: 2025-12-02
"""

import base64
import hashlib
import os
import secrets
from typing import Any, Optional, Union

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

from app.core.security_config import security_config


class EncryptionError(Exception):
    """Raised when encryption/decryption operations fail"""

    pass


class FieldEncryptor:
    """
    Field-level encryption using AES-256-GCM

    Features:
    - Authenticated encryption (prevents tampering)
    - Unique nonce for each encryption
    - Key derivation from master key
    - Base64 encoding for storage
    """

    ALGORITHM = "AES-256-GCM"
    KEY_SIZE = 32  # 256 bits
    NONCE_SIZE = 12  # 96 bits (recommended for GCM)

    def __init__(self, master_key: Optional[bytes] = None):
        """
        Initialize field encryptor

        Args:
            master_key: Optional master key (defaults to environment variable)
        """
        if master_key:
            self._master_key = master_key
        else:
            # Load from environment
            key_str = os.getenv("ENCRYPTION_KEY") or os.getenv("SECRET_KEY")
            if not key_str:
                raise EncryptionError("ENCRYPTION_KEY or SECRET_KEY must be set")

            # Derive encryption key from secret key
            self._master_key = self._derive_key(key_str.encode())

    def _derive_key(self, password: bytes, salt: Optional[bytes] = None) -> bytes:
        """
        Derive encryption key from password using PBKDF2

        Args:
            password: Password bytes
            salt: Optional salt (generated if not provided)

        Returns:
            Derived key bytes
        """
        if salt is None:
            # Use fixed salt for deterministic key derivation
            # In production, consider using per-organization salts stored securely
            salt = b"barq_encryption_salt_v1_do_not_change"

        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=self.KEY_SIZE,
            salt=salt,
            iterations=100000,
            backend=default_backend(),
        )

        return kdf.derive(password)

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext string

        Args:
            plaintext: String to encrypt

        Returns:
            Base64-encoded encrypted string with format: base64(nonce + ciphertext + tag)

        Raises:
            EncryptionError: If encryption fails
        """
        if not plaintext:
            return ""

        try:
            # Generate random nonce
            nonce = secrets.token_bytes(self.NONCE_SIZE)

            # Create cipher
            cipher = AESGCM(self._master_key)

            # Encrypt (returns ciphertext + authentication tag)
            ciphertext = cipher.encrypt(
                nonce, plaintext.encode("utf-8"), None  # No additional authenticated data
            )

            # Combine nonce + ciphertext for storage
            encrypted_data = nonce + ciphertext

            # Encode as base64 for storage
            return base64.b64encode(encrypted_data).decode("utf-8")

        except Exception as e:
            raise EncryptionError(f"Encryption failed: {str(e)}")

    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt encrypted string

        Args:
            encrypted_data: Base64-encoded encrypted string

        Returns:
            Decrypted plaintext string

        Raises:
            EncryptionError: If decryption fails (wrong key, tampered data, etc.)
        """
        if not encrypted_data:
            return ""

        try:
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_data)

            # Extract nonce and ciphertext
            nonce = encrypted_bytes[: self.NONCE_SIZE]
            ciphertext = encrypted_bytes[self.NONCE_SIZE :]

            # Create cipher
            cipher = AESGCM(self._master_key)

            # Decrypt (automatically verifies authentication tag)
            plaintext_bytes = cipher.decrypt(nonce, ciphertext, None)

            return plaintext_bytes.decode("utf-8")

        except Exception as e:
            raise EncryptionError(f"Decryption failed: {str(e)}")

    def encrypt_dict(self, data: dict, fields_to_encrypt: list) -> dict:
        """
        Encrypt specific fields in a dictionary

        Args:
            data: Dictionary containing data
            fields_to_encrypt: List of field names to encrypt

        Returns:
            Dictionary with encrypted fields
        """
        result = data.copy()

        for field in fields_to_encrypt:
            if field in result and result[field]:
                result[field] = self.encrypt(str(result[field]))

        return result

    def decrypt_dict(self, data: dict, fields_to_decrypt: list) -> dict:
        """
        Decrypt specific fields in a dictionary

        Args:
            data: Dictionary containing encrypted data
            fields_to_decrypt: List of field names to decrypt

        Returns:
            Dictionary with decrypted fields
        """
        result = data.copy()

        for field in fields_to_decrypt:
            if field in result and result[field]:
                try:
                    result[field] = self.decrypt(result[field])
                except EncryptionError:
                    # Keep encrypted value if decryption fails
                    pass

        return result


class DataMasker:
    """
    Data masking utilities for displaying sensitive information

    Masks data for display while keeping it usable for verification
    """

    @staticmethod
    def mask_email(email: str) -> str:
        """
        Mask email address

        Example: john.doe@example.com -> j***@example.com
        """
        if not email or "@" not in email:
            return email

        local, domain = email.split("@", 1)

        if len(local) <= 1:
            masked_local = "*"
        elif len(local) <= 3:
            masked_local = local[0] + "*" * (len(local) - 1)
        else:
            masked_local = local[0] + "*" * (len(local) - 2) + local[-1]

        return f"{masked_local}@{domain}"

    @staticmethod
    def mask_phone(phone: str, visible_digits: int = 4) -> str:
        """
        Mask phone number

        Example: +966501234567 -> +966*****4567
        """
        if not phone:
            return phone

        if len(phone) <= visible_digits:
            return "*" * len(phone)

        return (
            phone[:-visible_digits].replace(
                phone[:-visible_digits], "*" * len(phone[:-visible_digits])
            )
            + phone[-visible_digits:]
        )

    @staticmethod
    def mask_national_id(national_id: str) -> str:
        """
        Mask National ID

        Example: 1234567890 -> 1****7890
        """
        if not national_id:
            return national_id

        if len(national_id) <= 5:
            return "*" * len(national_id)

        return national_id[0] + "*" * (len(national_id) - 5) + national_id[-4:]

    @staticmethod
    def mask_iban(iban: str) -> str:
        """
        Mask IBAN

        Example: SA1234567890123456789012 -> SA********************9012
        """
        if not iban:
            return iban

        if len(iban) <= 6:
            return iban[:2] + "*" * (len(iban) - 2)

        return iban[:2] + "*" * (len(iban) - 6) + iban[-4:]

    @staticmethod
    def mask_card_number(card_number: str) -> str:
        """
        Mask credit card number

        Example: 1234567890123456 -> 1234********3456
        """
        if not card_number:
            return card_number

        # Remove spaces and dashes
        card_number = card_number.replace(" ", "").replace("-", "")

        if len(card_number) <= 8:
            return "*" * len(card_number)

        return card_number[:4] + "*" * (len(card_number) - 8) + card_number[-4:]

    @staticmethod
    def mask_string(value: str, visible_start: int = 2, visible_end: int = 2) -> str:
        """
        Generic string masking

        Args:
            value: String to mask
            visible_start: Number of characters to show at start
            visible_end: Number of characters to show at end

        Returns:
            Masked string
        """
        if not value:
            return value

        if len(value) <= (visible_start + visible_end):
            return "*" * len(value)

        masked_length = len(value) - visible_start - visible_end
        return value[:visible_start] + "*" * masked_length + value[-visible_end:]


class HashUtility:
    """
    One-way hashing utilities for data integrity and comparison

    Use for non-reversible data storage (e.g., checksum, fingerprints)
    """

    @staticmethod
    def sha256(data: Union[str, bytes]) -> str:
        """
        Generate SHA-256 hash

        Args:
            data: Data to hash

        Returns:
            Hex-encoded hash string
        """
        if isinstance(data, str):
            data = data.encode("utf-8")

        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def sha512(data: Union[str, bytes]) -> str:
        """Generate SHA-512 hash"""
        if isinstance(data, str):
            data = data.encode("utf-8")

        return hashlib.sha512(data).hexdigest()

    @staticmethod
    def hmac_sha256(data: Union[str, bytes], key: Union[str, bytes]) -> str:
        """
        Generate HMAC-SHA256

        Args:
            data: Data to hash
            key: Secret key

        Returns:
            Hex-encoded HMAC
        """
        import hmac

        if isinstance(data, str):
            data = data.encode("utf-8")
        if isinstance(key, str):
            key = key.encode("utf-8")

        return hmac.new(key, data, hashlib.sha256).hexdigest()


class EncryptedField:
    """
    SQLAlchemy custom type for encrypted fields

    Usage:
        class User(Base):
            national_id = Column(EncryptedField)
    """

    def __init__(self):
        self.encryptor = FieldEncryptor()

    def process_bind_param(self, value: Any, dialect) -> Optional[str]:
        """Encrypt value before storing in database"""
        if value is None:
            return None

        return self.encryptor.encrypt(str(value))

    def process_result_value(self, value: Any, dialect) -> Optional[str]:
        """Decrypt value when retrieving from database"""
        if value is None:
            return None

        try:
            return self.encryptor.decrypt(value)
        except EncryptionError:
            # Return encrypted value if decryption fails (for debugging)
            return f"[ENCRYPTED: {value[:20]}...]"


class SecureTokenGenerator:
    """
    Secure token generation for various purposes

    Use for:
    - Password reset tokens
    - Email verification tokens
    - API keys
    - Session tokens
    """

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """
        Generate cryptographically secure random token

        Args:
            length: Token length in bytes

        Returns:
            URL-safe token string
        """
        return secrets.token_urlsafe(length)

    @staticmethod
    def generate_hex_token(length: int = 32) -> str:
        """Generate hex-encoded token"""
        return secrets.token_hex(length)

    @staticmethod
    def generate_numeric_token(length: int = 6) -> str:
        """
        Generate numeric token (useful for OTP/verification codes)

        Args:
            length: Number of digits

        Returns:
            Numeric token string
        """
        # Generate random number with specified digits
        return "".join([str(secrets.randbelow(10)) for _ in range(length)])


# Global encryptor instance
_default_encryptor: Optional[FieldEncryptor] = None


def get_encryptor() -> FieldEncryptor:
    """
    Get global field encryptor instance

    Returns:
        FieldEncryptor instance
    """
    global _default_encryptor

    if _default_encryptor is None:
        _default_encryptor = FieldEncryptor()

    return _default_encryptor


def encrypt_field(plaintext: str) -> str:
    """Convenience function to encrypt a field"""
    return get_encryptor().encrypt(plaintext)


def decrypt_field(encrypted_data: str) -> str:
    """Convenience function to decrypt a field"""
    return get_encryptor().decrypt(encrypted_data)


def mask_sensitive_data(data: dict) -> dict:
    """
    Automatically mask sensitive fields in a dictionary

    Args:
        data: Dictionary potentially containing sensitive data

    Returns:
        Dictionary with masked sensitive fields
    """
    masked_data = data.copy()
    masker = DataMasker()

    sensitive_fields = {
        "email": masker.mask_email,
        "phone": masker.mask_phone,
        "mobile": masker.mask_phone,
        "national_id": masker.mask_national_id,
        "iban": masker.mask_iban,
        "bank_account": masker.mask_iban,
        "card_number": masker.mask_card_number,
    }

    for field, mask_func in sensitive_fields.items():
        if field in masked_data and masked_data[field]:
            try:
                masked_data[field] = mask_func(str(masked_data[field]))
            except:
                # If masking fails, replace with generic mask
                masked_data[field] = "***"

    return masked_data


# Auto-encrypt fields based on configuration
def should_encrypt_field(field_name: str) -> bool:
    """
    Check if a field should be encrypted based on configuration

    Args:
        field_name: Name of the field

    Returns:
        True if field should be encrypted
    """
    if not security_config.encryption.enable_field_encryption:
        return False

    return field_name in security_config.encryption.encrypted_fields
