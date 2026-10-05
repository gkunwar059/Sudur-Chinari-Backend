"""
Seed the header menu structure using the Category tree.

    python manage.py seed_menu_categories

Idempotent: safe to run multiple times. It:
  * creates a top-level "News" category,
  * sets menu order for existing top-level categories,
  * nests National / Agriculture / Technology under News,
  * creates Cricket / Football / Volleyball under Sports,
  * attaches thumbnail images from seed_assets/categories/ when a category has none.
"""
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from api.models import Category

ASSETS_DIR = Path(__file__).resolve().parent / "seed_assets" / "categories"

# (slug, name_en, name_ne, order, show_in_menu)
TOP_LEVEL = [
    ("news", "News", "समाचार", 10, True),
    ("politics", "Politics", "राजनीति", 20, True),
    ("society", "Society", "समाज", 30, True),
    ("economy", "Economy", "अर्थतन्त्र", 40, True),
    ("education", "Education", "शिक्षा", 50, True),
    ("health", "Health", "स्वास्थ्य", 60, True),
    ("sports", "Sports", "खेलकुद", 70, True),
    ("tourism", "Tourism", "पर्यटन", 80, True),
    ("opinion", "Opinion", "विचार", 90, True),
    # Kept as a category page, hidden from the header to keep the bar compact
    ("culture", "Culture", "संस्कृति", 100, False),
]

# parent_slug -> [(slug, name_en, name_ne, order)]
CHILDREN = {
    "news": [
        ("national", "National", "राष्ट्रिय", 10),
        ("agriculture", "Agriculture", "कृषि", 20),
        ("technology", "Technology", "प्रविधि", 30),
    ],
    "sports": [
        ("cricket", "Cricket", "क्रिकेट", 10),
        ("football", "Football", "फुटबल", 20),
        ("volleyball", "Volleyball", "भलिबल", 30),
    ],
}


class Command(BaseCommand):
    help = "Seed header menu categories and sub-categories."

    def _upsert(self, slug, name_en, name_ne, order, show_in_menu=True, parent=None):
        cat, created = Category.objects.get_or_create(
            slug=slug,
            defaults={"name_en": name_en, "name_ne": name_ne, "name": name_en},
        )
        cat.order = order
        cat.show_in_menu = show_in_menu
        cat.parent = parent
        if not cat.name_en:
            cat.name_en = name_en
        if not cat.name_ne:
            cat.name_ne = name_ne
        self._attach_image(cat)
        cat.save()
        self.stdout.write(f"  {'+' if created else '~'} {cat}")
        return cat

    def _attach_image(self, cat):
        if cat.image:
            return
        for ext in ("jpg", "jpeg", "png", "webp"):
            path = ASSETS_DIR / f"{cat.slug}.{ext}"
            if path.exists():
                with path.open("rb") as fh:
                    cat.image.save(path.name, File(fh), save=False)
                return

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Top-level menu items:")
        parents = {}
        for slug, en, ne, order, visible in TOP_LEVEL:
            parents[slug] = self._upsert(slug, en, ne, order, visible, parent=None)

        self.stdout.write("Sub-categories:")
        for parent_slug, kids in CHILDREN.items():
            for slug, en, ne, order in kids:
                self._upsert(slug, en, ne, order, True, parent=parents[parent_slug])

        # Push any other untouched top-level categories to the end of the menu
        known = {s for s, *_ in TOP_LEVEL} | {s for kids in CHILDREN.values() for s, *_ in kids}
        leftovers = Category.objects.filter(parent__isnull=True).exclude(slug__in=known).filter(order=0)
        updated = leftovers.update(order=1000)
        if updated:
            self.stdout.write(f"Moved {updated} other category(ies) to the end of the menu.")

        self.stdout.write(self.style.SUCCESS("Menu categories seeded."))
