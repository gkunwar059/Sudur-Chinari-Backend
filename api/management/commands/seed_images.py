from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont

from api.models import (
    Article,
    Category,
    District,
    DistrictPlace,
    DistrictSliderImage,
    Hotel,
    HotelGallery,
    HotelRoom,
    Partner,
    PhotoStory,
    PopupAd,
    VideoItem,
)

LATIN_SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
LATIN_SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
DEVA_SERIF = "/usr/share/fonts/truetype/noto/NotoSerifDevanagari-Bold.ttf"

FRONTEND_PUBLIC = Path(settings.BASE_DIR).parent / "news" / "public"

PALETTES = [
    ("#062B22", "#05965B", "#E8F5E9"),
    ("#072A44", "#0C6FB3", "#E3F2FD"),
    ("#3B1111", "#B91C1C", "#FDECEA"),
    ("#3B2A0B", "#B7791F", "#FDF6E3"),
    ("#1F2937", "#4B5563", "#F3F4F6"),
    ("#2D1B4E", "#6D28D9", "#EDE9FE"),
]


def hex_to_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def blend(color_a, color_b, amount):
    amount = max(0.0, min(1.0, amount))
    return tuple(
        int(color_a[i] + (color_b[i] - color_a[i]) * amount) for i in range(3)
    )


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def wrap_text(draw, text, font, max_width, max_lines=3):
    words = str(text).split()
    if not words:
        return []
    lines = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        box = draw.textbbox((0, 0), candidate, font=font)
        if box[2] - box[0] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
            if len(lines) >= max_lines:
                break
    if len(lines) < max_lines:
        lines.append(current)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
    if lines and len(lines) == max_lines:
        last_box = draw.textbbox((0, 0), lines[-1], font=font)
        if last_box[2] - last_box[0] > max_width:
            while lines[-1] and draw.textbbox((0, 0), lines[-1] + "…", font=font)[2] > max_width:
                lines[-1] = lines[-1][:-1].rstrip()
            lines[-1] = lines[-1] + "…"
    return lines


class Command(BaseCommand):
    help = "Generate placeholder images for seeded records and attach them to the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Regenerate images even when the target file already exists.",
        )

    def handle(self, *args, **options):
        self.force = options["force"]
        self.created = 0
        self.skipped = 0
        self.updated = 0

        self.stdout.write("Generating placeholder images...")
        self.ensure_districts()
        self.ensure_district_sliders()
        self.ensure_district_places()
        self.ensure_articles()
        self.ensure_hotels()
        self.ensure_hotel_rooms()
        self.ensure_hotel_galleries()
        self.ensure_partners()
        self.ensure_categories()
        self.ensure_videos()
        self.ensure_photo_stories()
        self.ensure_popup_ads()

        self.stdout.write(
            self.style.SUCCESS(
                f"Images ready: {self.created} created, {self.skipped} existing, "
                f"{self.updated} records updated."
            )
        )

    def has_local_image(self, value):
        name = str(getattr(value, "name", value) or "").strip()
        if not name:
            return False
        if name.startswith(("http://", "https://")):
            return "example.com" not in name
        return self.resolve_source(name) is not None

    def has_media_image(self, value):
        name = str(getattr(value, "name", value) or "").strip()
        if not name or name.startswith(("http://", "https://", "/")):
            return False
        return (Path(settings.MEDIA_ROOT) / name).is_file()

    def resolve_source(self, value):
        name = str(getattr(value, "name", value) or "").strip()
        if not name or name.startswith(("http://", "https://")):
            return None
        if name.startswith("/media/"):
            path = Path(settings.MEDIA_ROOT) / name[len("/media/") :]
        elif name.startswith("media/"):
            path = Path(settings.MEDIA_ROOT) / name[len("media/") :]
        elif name.startswith("/images/"):
            path = FRONTEND_PUBLIC / name.lstrip("/")
        elif name.startswith("images/"):
            path = FRONTEND_PUBLIC / name
        elif name.startswith("/"):
            path = Path(name)
        else:
            path = Path(settings.MEDIA_ROOT) / name
        return path if path.is_file() else None

    def ensure_image(self, kind, record_id, kicker, title, subtitle="", source=None):
        relative = Path("seed") / kind / f"{kind}-{record_id:03d}.jpg"
        target = Path(settings.MEDIA_ROOT) / relative
        if target.exists() and not self.force:
            self.skipped += 1
            return str(relative)

        target.parent.mkdir(parents=True, exist_ok=True)
        source_path = self.resolve_source(source) if source else None
        if source_path and not self.force:
            try:
                with Image.open(source_path) as image:
                    image = image.convert("RGB")
                    image.thumbnail((1400, 1400))
                    image.save(target, "JPEG", quality=85, optimize=True)
                self.created += 1
                return str(relative)
            except Exception:
                pass

        palette = PALETTES[record_id % len(PALETTES)]
        self.draw_placeholder(target, kicker, title, subtitle, record_id, palette)
        self.created += 1
        return str(relative)

    def draw_placeholder(self, target, kicker, title, subtitle, number, palette):
        width, height = 960, 540
        background = hex_to_rgb(palette[0])
        accent = hex_to_rgb(palette[1])
        light = hex_to_rgb(palette[2])
        ink = (248, 246, 242)

        image = Image.new("RGB", (width, height), background)
        draw = ImageDraw.Draw(image)
        for y in range(height):
            amount = (y / (height - 1)) ** 0.9 * 0.9
            draw.line([(0, y), (width, y)], fill=blend(background, accent, amount))

        draw.ellipse(
            [width * 0.58, -height * 0.45, width * 1.25, height * 0.75],
            fill=blend(accent, background, 0.35),
        )
        draw.ellipse(
            [width * 0.7, height * 0.15, width * 1.15, height * 1.1],
            fill=blend(accent, background, 0.15),
        )
        for offset in range(0, width, 64):
            shade = blend(accent, background, 0.45)
            draw.line(
                [(offset, height), (offset + height * 0.45, 0)], fill=shade, width=1
            )

        margin = int(width * 0.06)
        kicker_font = load_font(LATIN_SANS, 17)
        title_font = load_font(LATIN_SERIF, 54)
        subtitle_font = load_font(DEVA_SERIF, 24)
        footer_font = load_font(LATIN_SANS, 13)
        number_font = load_font(LATIN_SERIF, 150)

        draw.text((margin, margin), kicker.upper(), font=kicker_font, fill=light)
        draw.text(
            (width - margin, margin - 12),
            f"{number:02d}",
            font=number_font,
            fill=blend(accent, light, 0.55),
            anchor="ra",
        )
        draw.line(
            [(margin, margin + 34), (width - margin, margin + 34)],
            fill=blend(light, background, 0.35),
            width=2,
        )

        title_lines = wrap_text(draw, title, title_font, width - margin * 2)
        line_height = 64
        title_bottom = height - margin - 48
        title_top = title_bottom - len(title_lines) * line_height
        for i, line in enumerate(title_lines):
            draw.text(
                (margin, title_top + i * line_height),
                line,
                font=title_font,
                fill=ink,
            )

        if subtitle:
            subtitle_text = str(subtitle)
            while subtitle_text and draw.textbbox(
                (0, 0), subtitle_text, font=subtitle_font
            )[2] > width - margin * 2:
                subtitle_text = subtitle_text[:-1].rstrip()
            draw.text(
                (margin, title_bottom + 6),
                subtitle_text,
                font=subtitle_font,
                fill=blend(light, ink, 0.4),
            )

        draw.text(
            (margin, height - margin + 4),
            "SUDURPASHCHIM DIGITAL",
            font=footer_font,
            fill=blend(light, background, 0.15),
        )
        draw.line(
            [(margin, height - margin - 12), (width - margin, height - margin - 12)],
            fill=blend(light, background, 0.55),
            width=1,
        )

        image.save(target, "JPEG", quality=84, optimize=True)

    def save_field(self, instance, field, value):
        if str(getattr(instance, field)) == value:
            return
        setattr(instance, field, value)
        instance.save(update_fields=[field])
        self.updated += 1

    def ensure_districts(self):
        for district in District.objects.order_by("id"):
            if self.has_local_image(district.heroImage) and not self.force:
                continue
            relative = self.ensure_image(
                "districts",
                district.id,
                "District Profile",
                district.name_en or district.name or district.slug,
                district.name_ne or "",
                source=district.heroImage,
            )
            self.save_field(district, "heroImage", relative)

    def ensure_district_sliders(self):
        for slide in DistrictSliderImage.objects.select_related("district").order_by("id"):
            if self.has_media_image(slide.image) and not self.force:
                continue
            relative = self.ensure_image(
                "district-sliders",
                slide.id,
                "District Gallery",
                slide.district.name_en or slide.district.name or slide.district.slug,
                slide.district.name_ne or "",
                source=slide.image,
            )
            self.save_field(slide, "image", relative)

    def ensure_district_places(self):
        for place in DistrictPlace.objects.select_related("district").order_by("id"):
            if self.has_local_image(place.image) and not self.force:
                continue
            relative = self.ensure_image(
                "places",
                place.id,
                place.category.title() if place.category else "Place",
                place.title_en or place.title or "Place",
                place.district.name_ne or "",
                source=place.image,
            )
            self.save_field(place, "image", relative)

    def ensure_articles(self):
        for article in Article.objects.order_by("id"):
            if self.has_local_image(article.featuredImage) and not self.force:
                continue
            relative = self.ensure_image(
                "articles",
                article.id,
                "News",
                article.title_en or article.title or article.slug,
                article.title_ne or "",
                source=article.featuredImage,
            )
            self.save_field(article, "featuredImage", relative)

    def ensure_hotels(self):
        for hotel in Hotel.objects.select_related("district").order_by("id"):
            if self.has_media_image(hotel.hero_image) and not self.force:
                continue
            relative = self.ensure_image(
                "hotels",
                hotel.id,
                "Stay",
                hotel.name_en or hotel.name,
                hotel.name_ne or "",
                source=hotel.hero_image,
            )
            self.save_field(hotel, "hero_image", relative)

    def ensure_hotel_rooms(self):
        for room in HotelRoom.objects.select_related("hotel").order_by("id"):
            if self.has_media_image(room.image) and not self.force:
                continue
            relative = self.ensure_image(
                "hotel-rooms",
                room.id,
                "Room",
                room.name_en or room.name,
                room.hotel.name_ne or "",
                source=room.image,
            )
            self.save_field(room, "image", relative)

    def ensure_hotel_galleries(self):
        for gallery in HotelGallery.objects.select_related("hotel").order_by("id"):
            if self.has_media_image(gallery.image) and not self.force:
                continue
            relative = self.ensure_image(
                "hotel-gallery",
                gallery.id,
                "Gallery",
                gallery.hotel.name_en or gallery.hotel.name,
                gallery.hotel.name_ne or "",
                source=gallery.image,
            )
            self.save_field(gallery, "image", relative)

    def ensure_partners(self):
        for partner in Partner.objects.order_by("id"):
            if self.has_local_image(partner.image) and not self.force:
                continue
            relative = self.ensure_image(
                "partners",
                partner.id,
                "Partner",
                partner.name_en or partner.name,
                partner.role_en or partner.role,
                source=partner.image,
            )
            self.save_field(partner, "image", relative)

    def ensure_categories(self):
        for category in Category.objects.order_by("id"):
            if self.has_local_image(category.image) and not self.force:
                continue
            relative = self.ensure_image(
                "categories",
                category.id,
                "Section",
                category.name_en or category.name or category.slug,
                category.name_ne or "",
                source=category.image,
            )
            self.save_field(category, "image", relative)

    def ensure_videos(self):
        for video in VideoItem.objects.select_related("district").order_by("id"):
            if self.has_local_image(video.thumbnail) and not self.force:
                continue
            relative = self.ensure_image(
                "videos",
                video.id,
                "Video",
                video.title_en or video.title,
                video.district.name_ne if video.district else "",
                source=video.thumbnail,
            )
            self.save_field(video, "thumbnail", relative)

    def ensure_photo_stories(self):
        for story in PhotoStory.objects.select_related("district").order_by("id"):
            if self.has_local_image(story.coverImage) and not self.force:
                continue
            relative = self.ensure_image(
                "photo-stories",
                story.id,
                "Photo Story",
                story.title_en or story.title,
                story.district.name_ne if story.district else "",
                source=story.coverImage,
            )
            self.save_field(story, "coverImage", relative)

    def ensure_popup_ads(self):
        for ad in PopupAd.objects.order_by("id"):
            if self.has_media_image(ad.image) and not self.force:
                continue
            if not self.force and self.has_local_image(ad.image_url):
                continue
            relative = self.ensure_image(
                "ads",
                ad.id,
                "Advertisement",
                ad.title_en or ad.title,
                ad.advertiser or "",
                source=ad.image_url,
            )
            self.save_field(ad, "image", relative)
