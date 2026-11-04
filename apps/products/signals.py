import logging
from django.db.models.signals import post_migrate, pre_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

SYSTEM_PRODUCT_CATEGORIES = [
    {"slug": "dairy", "name_en": "Dairy", "name_ne": "दुग्धजन्य", "icon": "🥛", "order": 1},
    {"slug": "grains", "name_en": "Grains", "name_ne": "अन्न/धान्य", "icon": "🌾", "order": 2},
    {"slug": "fruits", "name_en": "Fruits", "name_ne": "फलफूल", "icon": "🍎", "order": 3},
    {"slug": "spices", "name_en": "Spices", "name_ne": "मसला/जडीबुटी", "icon": "🌿", "order": 4},
    {"slug": "handicrafts", "name_en": "Handicrafts", "name_ne": "हस्तकला", "icon": "🧵", "order": 5},
]

SYSTEM_PRODUCT_SLUGS = {cat["slug"] for cat in SYSTEM_PRODUCT_CATEGORIES}


@receiver(post_migrate)
def ensure_system_product_categories(sender, **kwargs):
    """
    Guarantees foundational product categories are always present
    whenever migrations run on any database.
    """
    if sender.name != 'apps.products':
        return

    from .models import ProductCategory

    for cat_data in SYSTEM_PRODUCT_CATEGORIES:
        slug = cat_data["slug"]
        defaults = {
            "name": cat_data["name_en"],
            "name_en": cat_data["name_en"],
            "name_ne": cat_data["name_ne"],
            "icon": cat_data["icon"],
            "order": cat_data["order"],
            "is_active": True,
            "is_system": True,
        }
        category, created = ProductCategory.objects.get_or_create(slug=slug, defaults=defaults)
        
        changed = False
        if not category.is_system:
            category.is_system = True
            changed = True
        if not category.is_active:
            category.is_active = True
            changed = True
        if changed:
            category.save(update_fields=['is_system', 'is_active'])
            logger.info("Updated system product category %s, is_system=True", slug)
        elif created:
            logger.info("Auto-seeded protected system product category: %s", slug)


@receiver(pre_delete)
def prevent_system_product_category_delete(sender, instance, **kwargs):
    """
    Intercepts and blocks deletion attempts on system product categories at signal level.
    """
    from .models import ProductCategory
    if sender is ProductCategory:
        if getattr(instance, 'is_system', False) or getattr(instance, 'slug', '') in SYSTEM_PRODUCT_SLUGS:
            raise ValidationError(
                f"Cannot delete protected product category '{instance.slug}'. "
                "This category is required by frontend product routes."
            )

