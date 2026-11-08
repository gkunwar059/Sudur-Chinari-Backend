import re
import uuid
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

NEPALI_DIGITS = str.maketrans('०१२३४५६७८९', '0123456789')

def validate_phone_number(phone):
    """
    Validates Nepal phone numbers (typically 10 digits starting with 98, 97, or 96).
    Accepts leading +977 or 977, spaces, dashes, parentheses, and Nepali numerals.
    Returns cleaned 10-digit number.
    """
    if not phone:
        raise ValidationError("Phone number is required.")
    
    cleaned = str(phone).strip().translate(NEPALI_DIGITS)
    cleaned = re.sub(r'[\s\-\(\)]', '', cleaned)
    if cleaned.startswith('+977'):
        cleaned = cleaned[4:]
    elif cleaned.startswith('977') and len(cleaned) == 13:
        cleaned = cleaned[3:]

    if not re.match(r'^(98|97|96)\d{8}$', cleaned):
        raise ValidationError("Enter a valid 10-digit Nepali mobile number (starting with 98, 97, or 96).")

    return cleaned


def generate_username_from_phone(phone):
    cleaned = str(phone).strip().translate(NEPALI_DIGITS)
    digits = re.sub(r'\D', '', cleaned)
    base = f"user_{digits[-10:]}"
    User = get_user_model()
    if not User.objects.filter(username=base).exists():
        return base
    return f"{base}_{uuid.uuid4().hex[:4]}"
