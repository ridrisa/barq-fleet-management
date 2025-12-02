"""
Comprehensive Input Validation Module

This module provides security-focused input validation including:
- Data sanitization (XSS prevention)
- Email validation
- Phone number validation
- File upload validation
- Date/time validation
- Custom validation rules
- SQL injection prevention helpers

Author: BARQ Security Team
Last Updated: 2025-12-02
"""

import re
import mimetypes
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

import bleach
from email_validator import validate_email, EmailNotValidError
from pydantic import validator


class SanitizationError(ValueError):
    """Raised when input sanitization fails"""
    pass


class ValidationError(ValueError):
    """Raised when input validation fails"""
    pass


class InputSanitizer:
    """
    Input sanitization utilities for XSS prevention and data cleaning

    All user inputs should be sanitized before storage and re-sanitized before display
    """

    # Allowed HTML tags for rich text (very restrictive)
    ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li']
    ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}
    ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']

    @classmethod
    def sanitize_html(
        cls,
        html_content: str,
        strip_tags: bool = False,
        allowed_tags: Optional[List[str]] = None,
        allowed_attributes: Optional[Dict[str, List[str]]] = None
    ) -> str:
        """
        Sanitize HTML content to prevent XSS attacks

        Args:
            html_content: Raw HTML content
            strip_tags: If True, remove all HTML tags
            allowed_tags: Override default allowed tags
            allowed_attributes: Override default allowed attributes

        Returns:
            Sanitized HTML string
        """
        if not html_content:
            return ""

        if strip_tags:
            return bleach.clean(html_content, tags=[], strip=True)

        tags = allowed_tags or cls.ALLOWED_TAGS
        attrs = allowed_attributes or cls.ALLOWED_ATTRIBUTES

        return bleach.clean(
            html_content,
            tags=tags,
            attributes=attrs,
            protocols=cls.ALLOWED_PROTOCOLS,
            strip=True
        )

    @staticmethod
    def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize plain text string

        Args:
            value: Input string
            max_length: Optional maximum length

        Returns:
            Sanitized string
        """
        if not value:
            return ""

        # Remove null bytes
        value = value.replace('\x00', '')

        # Strip leading/trailing whitespace
        value = value.strip()

        # Normalize whitespace
        value = re.sub(r'\s+', ' ', value)

        # Truncate if needed
        if max_length and len(value) > max_length:
            value = value[:max_length]

        return value

    @staticmethod
    def sanitize_sql_identifier(identifier: str) -> str:
        """
        Sanitize SQL identifier (table/column name)

        Args:
            identifier: SQL identifier

        Returns:
            Sanitized identifier

        Raises:
            SanitizationError: If identifier contains invalid characters
        """
        # Only allow alphanumeric and underscore
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
            raise SanitizationError(
                f"Invalid SQL identifier: {identifier}. Only alphanumeric and underscore allowed."
            )

        # Prevent SQL reserved keywords (basic check)
        sql_keywords = {
            'select', 'insert', 'update', 'delete', 'drop', 'create',
            'alter', 'truncate', 'union', 'join', 'where', 'from', 'table'
        }

        if identifier.lower() in sql_keywords:
            raise SanitizationError(f"SQL reserved keyword not allowed: {identifier}")

        return identifier

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename for safe storage

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove path components
        filename = Path(filename).name

        # Remove or replace dangerous characters
        filename = re.sub(r'[^\w\s\-\.]', '_', filename)

        # Prevent directory traversal
        filename = filename.replace('..', '_')

        # Limit length
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + ('.' + ext if ext else '')

        return filename


class EmailValidator:
    """Email validation utilities"""

    @staticmethod
    def validate(email: str, check_deliverability: bool = False) -> Dict[str, Any]:
        """
        Validate email address

        Args:
            email: Email address to validate
            check_deliverability: Check if domain has MX records

        Returns:
            Dict with validation results

        Raises:
            ValidationError: If email is invalid
        """
        try:
            result = validate_email(
                email,
                check_deliverability=check_deliverability
            )

            return {
                "valid": True,
                "normalized": result.normalized,
                "local_part": result.local_part,
                "domain": result.domain,
                "ascii_email": result.ascii_email,
            }

        except EmailNotValidError as e:
            raise ValidationError(f"Invalid email address: {str(e)}")

    @staticmethod
    def is_valid(email: str) -> bool:
        """Quick email validation check"""
        try:
            EmailValidator.validate(email)
            return True
        except ValidationError:
            return False


class PhoneValidator:
    """Phone number validation utilities (Saudi Arabia focus)"""

    # Saudi Arabia phone patterns
    SAUDI_MOBILE_PATTERN = r'^(009665|9665|\+9665|05|5)(5|0|3|6|4|9|1|8|7)([0-9]{7})$'
    SAUDI_LANDLINE_PATTERN = r'^(009661|9661|\+9661|01|1)([0-9]{7})$'

    @classmethod
    def validate_saudi_mobile(cls, phone: str) -> Dict[str, Any]:
        """
        Validate Saudi mobile number

        Args:
            phone: Phone number to validate

        Returns:
            Dict with validation results
        """
        # Remove spaces and dashes
        phone = re.sub(r'[\s\-]', '', phone)

        if re.match(cls.SAUDI_MOBILE_PATTERN, phone):
            # Normalize to international format
            normalized = cls._normalize_saudi_mobile(phone)
            return {
                "valid": True,
                "normalized": normalized,
                "type": "mobile",
                "country": "SA"
            }

        raise ValidationError(f"Invalid Saudi mobile number: {phone}")

    @classmethod
    def validate_saudi_landline(cls, phone: str) -> Dict[str, Any]:
        """Validate Saudi landline number"""
        phone = re.sub(r'[\s\-]', '', phone)

        if re.match(cls.SAUDI_LANDLINE_PATTERN, phone):
            normalized = cls._normalize_saudi_landline(phone)
            return {
                "valid": True,
                "normalized": normalized,
                "type": "landline",
                "country": "SA"
            }

        raise ValidationError(f"Invalid Saudi landline number: {phone}")

    @classmethod
    def validate(cls, phone: str, phone_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate phone number (auto-detect type)

        Args:
            phone: Phone number
            phone_type: Optional type hint ("mobile" or "landline")

        Returns:
            Validation result dict
        """
        if phone_type == "mobile":
            return cls.validate_saudi_mobile(phone)
        elif phone_type == "landline":
            return cls.validate_saudi_landline(phone)

        # Auto-detect
        try:
            return cls.validate_saudi_mobile(phone)
        except ValidationError:
            try:
                return cls.validate_saudi_landline(phone)
            except ValidationError:
                raise ValidationError(f"Invalid phone number: {phone}")

    @staticmethod
    def _normalize_saudi_mobile(phone: str) -> str:
        """Normalize Saudi mobile to +966 format"""
        # Extract digits only
        digits = re.sub(r'\D', '', phone)

        # Handle different formats
        if digits.startswith('00966'):
            digits = digits[2:]
        elif digits.startswith('966'):
            pass
        elif digits.startswith('0'):
            digits = '966' + digits[1:]
        elif len(digits) == 9:
            digits = '966' + digits

        return '+' + digits

    @staticmethod
    def _normalize_saudi_landline(phone: str) -> str:
        """Normalize Saudi landline to +966 format"""
        digits = re.sub(r'\D', '', phone)

        if digits.startswith('00966'):
            digits = digits[2:]
        elif digits.startswith('966'):
            pass
        elif digits.startswith('0'):
            digits = '966' + digits[1:]

        return '+' + digits


class FileValidator:
    """File upload validation utilities"""

    # Allowed MIME types
    ALLOWED_IMAGE_TYPES = {
        'image/jpeg', 'image/png', 'image/gif', 'image/webp'
    }

    ALLOWED_DOCUMENT_TYPES = {
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }

    # Maximum file sizes (in bytes)
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
    MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10 MB
    MAX_GENERAL_SIZE = 20 * 1024 * 1024  # 20 MB

    @classmethod
    def validate_image(
        cls,
        filename: str,
        content_type: str,
        size: int
    ) -> Dict[str, Any]:
        """
        Validate image upload

        Args:
            filename: Original filename
            content_type: MIME type
            size: File size in bytes

        Returns:
            Validation result dict

        Raises:
            ValidationError: If validation fails
        """
        # Check MIME type
        if content_type not in cls.ALLOWED_IMAGE_TYPES:
            raise ValidationError(
                f"Invalid image type. Allowed: {', '.join(cls.ALLOWED_IMAGE_TYPES)}"
            )

        # Check file size
        if size > cls.MAX_IMAGE_SIZE:
            raise ValidationError(
                f"Image too large. Maximum: {cls.MAX_IMAGE_SIZE / 1024 / 1024:.1f} MB"
            )

        # Check file extension matches MIME type
        ext = Path(filename).suffix.lower()
        expected_ext = mimetypes.guess_extension(content_type)

        if expected_ext and ext != expected_ext:
            raise ValidationError(
                f"File extension mismatch. Expected {expected_ext}, got {ext}"
            )

        return {
            "valid": True,
            "sanitized_filename": InputSanitizer.sanitize_filename(filename),
            "content_type": content_type,
            "size": size
        }

    @classmethod
    def validate_document(
        cls,
        filename: str,
        content_type: str,
        size: int
    ) -> Dict[str, Any]:
        """Validate document upload"""
        if content_type not in cls.ALLOWED_DOCUMENT_TYPES:
            raise ValidationError(
                f"Invalid document type. Allowed: {', '.join(cls.ALLOWED_DOCUMENT_TYPES)}"
            )

        if size > cls.MAX_DOCUMENT_SIZE:
            raise ValidationError(
                f"Document too large. Maximum: {cls.MAX_DOCUMENT_SIZE / 1024 / 1024:.1f} MB"
            )

        return {
            "valid": True,
            "sanitized_filename": InputSanitizer.sanitize_filename(filename),
            "content_type": content_type,
            "size": size
        }


class DateTimeValidator:
    """Date and time validation utilities"""

    @staticmethod
    def validate_date(
        date_str: str,
        format: str = "%Y-%m-%d",
        min_date: Optional[date] = None,
        max_date: Optional[date] = None
    ) -> date:
        """
        Validate date string

        Args:
            date_str: Date string
            format: Expected date format
            min_date: Minimum allowed date
            max_date: Maximum allowed date

        Returns:
            Parsed date object

        Raises:
            ValidationError: If validation fails
        """
        try:
            parsed_date = datetime.strptime(date_str, format).date()

            if min_date and parsed_date < min_date:
                raise ValidationError(f"Date cannot be before {min_date}")

            if max_date and parsed_date > max_date:
                raise ValidationError(f"Date cannot be after {max_date}")

            return parsed_date

        except ValueError as e:
            raise ValidationError(f"Invalid date format: {str(e)}")

    @staticmethod
    def validate_datetime(
        datetime_str: str,
        format: str = "%Y-%m-%d %H:%M:%S",
        min_datetime: Optional[datetime] = None,
        max_datetime: Optional[datetime] = None
    ) -> datetime:
        """Validate datetime string"""
        try:
            parsed_dt = datetime.strptime(datetime_str, format)

            if min_datetime and parsed_dt < min_datetime:
                raise ValidationError(f"Datetime cannot be before {min_datetime}")

            if max_datetime and parsed_dt > max_datetime:
                raise ValidationError(f"Datetime cannot be after {max_datetime}")

            return parsed_dt

        except ValueError as e:
            raise ValidationError(f"Invalid datetime format: {str(e)}")

    @staticmethod
    def validate_future_date(date_obj: Union[date, datetime]) -> bool:
        """Check if date is in the future"""
        today = date.today() if isinstance(date_obj, date) else datetime.now()
        return date_obj > today

    @staticmethod
    def validate_past_date(date_obj: Union[date, datetime]) -> bool:
        """Check if date is in the past"""
        today = date.today() if isinstance(date_obj, date) else datetime.now()
        return date_obj < today


class NationalIDValidator:
    """Saudi National ID validation"""

    NATIONAL_ID_PATTERN = r'^[12]\d{9}$'

    @classmethod
    def validate(cls, national_id: str) -> Dict[str, Any]:
        """
        Validate Saudi National ID

        Args:
            national_id: National ID number

        Returns:
            Validation result dict

        Raises:
            ValidationError: If invalid
        """
        # Remove spaces and dashes
        national_id = re.sub(r'[\s\-]', '', national_id)

        if not re.match(cls.NATIONAL_ID_PATTERN, national_id):
            raise ValidationError(
                "Invalid National ID. Must be 10 digits starting with 1 or 2"
            )

        # First digit indicates nationality (1=Saudi, 2=Non-Saudi)
        nationality = "Saudi" if national_id[0] == "1" else "Non-Saudi"

        return {
            "valid": True,
            "normalized": national_id,
            "nationality": nationality
        }


class IBANValidator:
    """IBAN validation (Saudi Arabia)"""

    SAUDI_IBAN_PATTERN = r'^SA\d{22}$'

    @classmethod
    def validate(cls, iban: str) -> Dict[str, Any]:
        """
        Validate Saudi IBAN

        Args:
            iban: IBAN string

        Returns:
            Validation result dict

        Raises:
            ValidationError: If invalid
        """
        # Remove spaces
        iban = iban.replace(' ', '').upper()

        if not re.match(cls.SAUDI_IBAN_PATTERN, iban):
            raise ValidationError(
                "Invalid Saudi IBAN. Must be SA followed by 22 digits"
            )

        # Verify checksum (IBAN mod 97 algorithm)
        if not cls._verify_iban_checksum(iban):
            raise ValidationError("Invalid IBAN checksum")

        return {
            "valid": True,
            "normalized": iban,
            "country": "SA"
        }

    @staticmethod
    def _verify_iban_checksum(iban: str) -> bool:
        """Verify IBAN checksum using mod 97 algorithm"""
        # Move first 4 characters to end
        rearranged = iban[4:] + iban[:4]

        # Replace letters with numbers (A=10, B=11, ..., Z=35)
        numeric = ''
        for char in rearranged:
            if char.isdigit():
                numeric += char
            else:
                numeric += str(ord(char) - ord('A') + 10)

        # Check if mod 97 equals 1
        return int(numeric) % 97 == 1


class CustomValidators:
    """Custom validation utilities for common patterns"""

    @staticmethod
    def validate_license_plate(plate: str) -> Dict[str, Any]:
        """Validate Saudi license plate format"""
        # Saudi plates: XXX 1234 (3 Arabic letters + 4 digits)
        # For now, accept alphanumeric
        plate = plate.upper().replace(' ', '')

        if not re.match(r'^[A-Z0-9]{4,8}$', plate):
            raise ValidationError("Invalid license plate format")

        return {
            "valid": True,
            "normalized": plate
        }

    @staticmethod
    def validate_vin(vin: str) -> Dict[str, Any]:
        """Validate Vehicle Identification Number (VIN)"""
        vin = vin.upper().replace(' ', '')

        # VIN is 17 characters, excludes I, O, Q
        if not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', vin):
            raise ValidationError("Invalid VIN format (must be 17 characters, no I/O/Q)")

        return {
            "valid": True,
            "normalized": vin
        }

    @staticmethod
    def validate_postal_code(postal_code: str, country: str = "SA") -> Dict[str, Any]:
        """Validate postal code"""
        postal_code = postal_code.replace(' ', '').replace('-', '')

        if country == "SA":
            # Saudi postal code: 5 digits + optional 4 digits
            if not re.match(r'^\d{5}(\d{4})?$', postal_code):
                raise ValidationError("Invalid Saudi postal code (must be 5 or 9 digits)")

        return {
            "valid": True,
            "normalized": postal_code,
            "country": country
        }


# SQL Injection Prevention Helpers
class SQLSafetyChecker:
    """SQL injection prevention utilities"""

    DANGEROUS_PATTERNS = [
        r"('\s*(or|and)\s*')",
        r"(--|\#|\/\*|\*\/)",
        r"(union\s+select)",
        r"(drop\s+table)",
        r"(insert\s+into)",
        r"(delete\s+from)",
        r"(update\s+\w+\s+set)",
        r"(exec\s*\()",
        r"(execute\s*\()",
    ]

    @classmethod
    def is_safe(cls, user_input: str) -> bool:
        """
        Check if input is safe from SQL injection

        Note: This is a backup check. Always use parameterized queries!
        """
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, user_input, re.IGNORECASE):
                return False
        return True

    @classmethod
    def check_and_raise(cls, user_input: str):
        """Check input and raise error if unsafe"""
        if not cls.is_safe(user_input):
            raise ValidationError("Input contains potentially dangerous SQL patterns")
