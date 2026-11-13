from django.db import migrations, models
from django.utils.text import slugify


def populate_district_place_slugs(apps, schema_editor):
    DistrictPlace = apps.get_model("districts", "DistrictPlace")
    used = set()
    for place in DistrictPlace.objects.select_related("district").order_by("id"):
        if place.slug and place.slug not in used:
            used.add(place.slug)
            continue

        raw_title = getattr(place, "title_en", None) or place.title or ""
        district_slug = place.district.slug if place.district_id and place.district else "place"
        base = slugify(raw_title) or f"{district_slug}-place"
        base = base[:240]
        candidate = base
        counter = 1
        while candidate in used:
            suffix = f"-{counter}"
            candidate = f"{base[:255 - len(suffix)]}{suffix}"
            counter += 1

        used.add(candidate)
        place.slug = candidate
        place.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("districts", "0005_alter_storysubmission_main_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="districtplace",
            name="slug",
            field=models.SlugField(blank=True, max_length=255, null=True),
        ),
        migrations.RunPython(
            populate_district_place_slugs,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="districtplace",
            name="slug",
            field=models.SlugField(blank=True, max_length=255, unique=True),
        ),
    ]

