import logging
from django.db.models.signals import post_migrate, pre_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

SYSTEM_CATEGORIES = [
    {
        "slug": "politics",
        "name_en": "Politics",
        "name_ne": "राजनीति",
        "icon": "🏛️",
        "layout_type": "politics",
        "order": 10,
        "show_in_menu": True,
    },
    {
        "slug": "society",
        "name_en": "Society",
        "name_ne": "समाज",
        "icon": "👥",
        "layout_type": "default",
        "order": 20,
        "show_in_menu": True,
    },
    {
        "slug": "economy",
        "name_en": "Economy",
        "name_ne": "अर्थतन्त्र",
        "icon": "📈",
        "layout_type": "default",
        "order": 30,
        "show_in_menu": True,
    },
    {
        "slug": "education",
        "name_en": "Education",
        "name_ne": "शिक्षा",
        "icon": "📚",
        "layout_type": "default",
        "order": 40,
        "show_in_menu": True,
    },
    {
        "slug": "health",
        "name_en": "Health",
        "name_ne": "स्वास्थ्य",
        "icon": "🏥",
        "layout_type": "default",
        "order": 50,
        "show_in_menu": True,
    },
    {
        "slug": "sports",
        "name_en": "Sports",
        "name_ne": "खेलकुद",
        "icon": "⚽",
        "layout_type": "sports",
        "order": 60,
        "show_in_menu": True,
    },
    {
        "slug": "culture",
        "name_en": "Culture",
        "name_ne": "संस्कृति",
        "icon": "🎭",
        "layout_type": "default",
        "order": 70,
        "show_in_menu": True,
    },
    {
        "slug": "tourism",
        "name_en": "Tourism",
        "name_ne": "पर्यटन",
        "icon": "🏔️",
        "layout_type": "tourism",
        "order": 80,
        "show_in_menu": True,
    },
    {
        "slug": "opinion",
        "name_en": "Opinion",
        "name_ne": "विचार",
        "icon": "✍️",
        "layout_type": "default",
        "order": 90,
        "show_in_menu": True,
    },
    {
        "slug": "agriculture",
        "name_en": "Agriculture",
        "name_ne": "कृषि",
        "icon": "🌾",
        "layout_type": "default",
        "order": 100,
        "show_in_menu": True,
    },
    {
        "slug": "technology",
        "name_en": "Technology",
        "name_ne": "प्रविधि",
        "icon": "💻",
        "layout_type": "default",
        "order": 110,
        "show_in_menu": True,
    },
    {
        "slug": "national",
        "name_en": "National",
        "name_ne": "राष्ट्रिय",
        "icon": "🇳🇵",
        "layout_type": "default",
        "order": 120,
        "show_in_menu": True,
    },
    {
        "slug": "news",
        "name_en": "News",
        "name_ne": "समाचार",
        "icon": "📰",
        "layout_type": "news",
        "order": 130,
        "show_in_menu": True,
    },
    {
        "slug": "stay",
        "name_en": "Hotels & Stay",
        "name_ne": "होटल तथा बासस्थान",
        "icon": "🏨",
        "layout_type": "stay",
        "order": 140,
        "show_in_menu": True,
    },
]

SYSTEM_SLUGS = {cat["slug"] for cat in SYSTEM_CATEGORIES}


@receiver(post_migrate)
def ensure_system_categories(sender, **kwargs):
    """
    Guarantees foundational system categories are always present with correct layout types
    whenever migrations run on any database.
    """
    if sender.name != 'apps.articles':
        return

    from .models import Category

    for cat_data in SYSTEM_CATEGORIES:
        slug = cat_data["slug"]
        defaults = {
            "name": cat_data["name_en"],
            "name_en": cat_data["name_en"],
            "name_ne": cat_data["name_ne"],
            "icon": cat_data["icon"],
            "layout_type": cat_data["layout_type"],
            "order": cat_data["order"],
            "show_in_menu": cat_data["show_in_menu"],
            "is_system": True,
        }
        category, created = Category.objects.get_or_create(slug=slug, defaults=defaults)
        
        # Ensure system flag and layout type stay in sync even if already created
        changed = False
        if not category.is_system:
            category.is_system = True
            changed = True
        if category.layout_type != cat_data["layout_type"]:
            category.layout_type = cat_data["layout_type"]
            changed = True
        if changed:
            category.save(update_fields=['is_system', 'layout_type'])
            logger.info("Updated system category %s to layout_type=%s, is_system=True", slug, cat_data["layout_type"])
        elif created:
            logger.info("Auto-seeded protected system category: %s", slug)


@receiver(pre_delete)
def prevent_system_category_delete(sender, instance, **kwargs):
    """
    Intercepts and blocks deletion attempts on system categories at the signal level.
    """
    # Check if instance is a Category
    from .models import Category
    if sender is Category:
        if getattr(instance, 'is_system', False) or getattr(instance, 'slug', '') in SYSTEM_SLUGS:
            raise ValidationError(
                f"Cannot delete protected system category '{instance.slug}'. "
                "This category is required by frontend application routes."
            )
