"""
Input Sanitization Utilities
Prevents XSS and injection attacks
"""

import re
from typing import Any, Dict, List, Optional, Union
import bleach

# Allowed HTML tags (for rich text fields)
ALLOWED_TAGS = ['b', 'i', 'u', 'strong', 'em', 'br', 'p', 'ul', 'ol', 'li']
ALLOWED_ATTRIBUTES = {}

# Strict mode - no HTML at all
STRICT_TAGS = []
STRICT_ATTRIBUTES = {}


def sanitize_html(text: str, strict: bool = True) -> str:
    """
    Sanitize HTML from text input.
    
    Args:
        text: Input text that may contain HTML
        strict: If True, removes ALL HTML. If False, allows safe tags.
    
    Returns:
        Sanitized text
    """
    if not text:
        return text
    
    if strict:
        return bleach.clean(text, tags=STRICT_TAGS, attributes=STRICT_ATTRIBUTES, strip=True)
    else:
        return bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)


def sanitize_string(text: str) -> str:
    """
    Sanitize a plain text string - removes all HTML and trims whitespace.
    """
    if not text:
        return text
    
    # Remove HTML
    cleaned = bleach.clean(text, tags=[], attributes={}, strip=True)
    
    # Normalize whitespace
    cleaned = ' '.join(cleaned.split())
    
    return cleaned.strip()


def sanitize_dict(data: Dict[str, Any], string_fields: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Sanitize all string fields in a dictionary.
    
    Args:
        data: Dictionary to sanitize
        string_fields: Optional list of fields to sanitize. If None, sanitizes all string fields.
    
    Returns:
        Sanitized dictionary
    """
    result = {}
    for key, value in data.items():
        if isinstance(value, str):
            if string_fields is None or key in string_fields:
                result[key] = sanitize_string(value)
            else:
                result[key] = value
        elif isinstance(value, dict):
            result[key] = sanitize_dict(value, string_fields)
        elif isinstance(value, list):
            result[key] = [
                sanitize_string(item) if isinstance(item, str) else item
                for item in value
            ]
        else:
            result[key] = value
    return result


def validate_no_script(text: str) -> bool:
    """
    Check if text contains potential script injection.
    Returns True if safe, False if suspicious.
    """
    if not text:
        return True
    
    # Common XSS patterns
    suspicious_patterns = [
        r'<script',
        r'javascript:',
        r'on\w+\s*=',  # onclick, onerror, etc.
        r'eval\s*\(',
        r'document\.',
        r'window\.',
        r'<iframe',
        r'<object',
        r'<embed',
        r'<link\s+rel\s*=',
        r'expression\s*\(',
        r'url\s*\(',
    ]
    
    text_lower = text.lower()
    for pattern in suspicious_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return False
    
    return True


def sanitize_email(email: str) -> str:
    """Sanitize email address"""
    if not email:
        return email
    return bleach.clean(email, tags=[], strip=True).strip().lower()


def sanitize_phone(phone: str) -> str:
    """Sanitize phone number - keep only digits, +, -, and spaces"""
    if not phone:
        return phone
    return re.sub(r'[^\d\+\-\s]', '', phone).strip()


# Example usage in Pydantic validators
def create_sanitized_validator(field_name: str):
    """Create a Pydantic validator that sanitizes input"""
    def validator(cls, v):
        if isinstance(v, str):
            sanitized = sanitize_string(v)
            if not validate_no_script(sanitized):
                raise ValueError(f"Invalid characters detected in {field_name}")
            return sanitized
        return v
    return validator
