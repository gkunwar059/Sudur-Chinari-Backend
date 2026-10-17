"""
Backward compatibility layer for utilities.
Now organized in:
- apps.common.pagination (StandardResultsSetPagination)
- apps.common.serializers_base (make_absolute_url, get_bilingual_or_localized, TranslatedAdminSerializerMixin)
- apps.accounts.utils (validate_phone_number, generate_username_from_phone)
"""

from apps.common.pagination import StandardResultsSetPagination
from apps.common.serializers_base import (
    make_absolute_url,
    get_bilingual_or_localized,
    TranslatedAdminSerializerMixin,
)
from apps.accounts.utils import (
    validate_phone_number,
    generate_username_from_phone,
)

__all__ = [
    'StandardResultsSetPagination',
    'make_absolute_url',
    'get_bilingual_or_localized',
    'TranslatedAdminSerializerMixin',
    'validate_phone_number',
    'generate_username_from_phone',
]
