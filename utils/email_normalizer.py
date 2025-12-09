"""Email normalization utilities for converting spoken email format to proper email address."""

import re
import logging

logger = logging.getLogger(__name__)


def normalize_email(email_str: str) -> str:
    """
    Convert spoken/natural language email format to proper email address.

    Examples:
        "Mohid Youssef four five six at Gmail dot com" -> "mohidyoussef456@gmail.com"
        "john.doe at example dot com" -> "john.doe@example.com"
        "test_user123 at yahoo dot co dot uk" -> "test_user123@yahoo.co.uk"

    Args:
        email_str: Email address in spoken or written format

    Returns:
        Normalized email address in proper format (lowercase, @ and . symbols)
    """
    if not email_str:
        return email_str

    # If already a valid email format (contains @), return as-is (lowercased)
    if '@' in email_str and '.' in email_str.split('@')[1]:
        return email_str.lower().strip()

    logger.info(f"Normalizing spoken email format: {email_str}")

    # Convert to lowercase and strip whitespace
    email = email_str.lower().strip()

    # Replace common spoken phrases with proper symbols
    replacements = [
        # @ symbol variations
        (r'\bat\b', '@'),
        (r'\bat sign\b', '@'),
        (r'\s*@\s*', '@'),  # Clean up spacing around @

        # . (dot) variations
        (r'\bdot\b', '.'),
        (r'\bpoint\b', '.'),
        (r'\s*\.\s*', '.'),  # Clean up spacing around dots
    ]

    for pattern, replacement in replacements:
        email = re.sub(pattern, replacement, email)

    # Convert number words to digits
    number_words = {
        'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
        'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
    }

    # Replace word numbers with digits (case insensitive, word boundaries)
    for word, digit in number_words.items():
        email = re.sub(rf'\b{word}\b', digit, email, flags=re.IGNORECASE)

    # Remove all remaining spaces
    email = email.replace(' ', '')

    # Validate basic email structure after normalization
    if '@' not in email:
        logger.warning(f"Normalized email missing @: {email}")
        # Try to find where @ should be (common pattern: text at text)
        # This is a fallback - should rarely happen
        parts = email.split('at', 1)
        if len(parts) == 2:
            email = f"{parts[0]}@{parts[1]}"

    logger.info(f"Normalized to: {email}")
    return email


def extract_email_components(email_str: str) -> dict:
    """
    Extract components from email for debugging/validation.

    Returns dict with keys: local_part, domain, tld
    """
    normalized = normalize_email(email_str)

    if '@' not in normalized:
        return {'local_part': None, 'domain': None, 'tld': None, 'normalized': normalized}

    local, domain_part = normalized.split('@', 1)
    domain_parts = domain_part.split('.')

    return {
        'local_part': local,
        'domain': '.'.join(domain_parts[:-1]) if len(domain_parts) > 1 else domain_part,
        'tld': domain_parts[-1] if len(domain_parts) > 1 else None,
        'normalized': normalized
    }
