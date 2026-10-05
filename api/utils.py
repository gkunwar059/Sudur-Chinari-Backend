import re
import uuid
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

def validate_phone_number(value: str) -> str:
    """
    Validates phone number format and returns cleaned representation.
    Accepts international format with leading '+', or local digits (7-15 digits).
    """
    if not value:
        raise ValidationError("Phone number is required.")
    
    cleaned = re.sub(r'[\s\-\(\)]', '', str(value).strip())
    if not re.match(r'^\+?[0-9]{7,15}$', cleaned):
        raise ValidationError("Enter a valid phone number (7 to 15 digits).")
    
    return cleaned


def generate_username_from_phone(phone: str) -> str:
    """
    Generates a unique username from a phone number.
    e.g., '9841234567' -> 'user_9841234567'
    Appends counter suffix if duplicate exists.
    """
    digits = re.sub(r'\D', '', str(phone or ''))
    base = f"user_{digits}" if digits else f"user_{uuid.uuid4().hex[:8]}"
    username = base
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base}_{counter}"
        counter += 1
    return username
