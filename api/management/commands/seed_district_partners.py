import math
import os
from PIL import Image, ImageDraw, ImageFont
from django.core.management.base import BaseCommand
from django.conf import settings
from api.models import Partner, District


def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


F_SANS_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
F_SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"


def draw_centered_text(draw, text, cx, cy, font, fill="#FFFFFF"):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((cx - w / 2, cy - h / 2), text, font=font, fill=fill)


def draw_badge_base(bg_color, rim_color, inner_rim=None):
    img = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([32, 32, 992, 992], fill=bg_color, outline=rim_color, width=16)
    if inner_rim:
        d.ellipse([64, 64, 960, 960], outline=inner_rim, width=4)
        d.ellipse([88, 88, 936, 936], outline=rim_color, width=2)
    return img, d


def make_kailali_partner_logo():
    img, d = draw_badge_base("#064E3B", "#F59E0B", "#FDE047")
    cx, cy = 512, 420
    # Center gear & trade handshake
    d.ellipse([cx - 200, cy - 200, cx + 200, cy + 200], fill="#047857", outline="#F59E0B", width=6)
    # Gear teeth
    for a in range(0, 360, 30):
        rad = math.radians(a)
        x1 = cx + 180 * math.cos(rad)
        y1 = cy + 180 * math.sin(rad)
        x2 = cx + 220 * math.cos(rad)
        y2 = cy + 220 * math.sin(rad)
        d.line([(x1, y1), (x2, y2)], fill="#F59E0B", width=14)
    # Handshake / bridge symbol (Karnali bridge arch + trade hands)
    d.arc([cx - 140, cy - 130, cx + 140, cy + 90], 180, 360, fill="#FFFFFF", width=10)
    d.rectangle([cx - 80, cy, cx + 80, cy + 60], fill="#F59E0B")
    d.line([(cx - 100, cy + 30), (cx + 100, cy + 30)], fill="#064E3B", width=6)

    f_title = get_font(F_SANS_BOLD, 46)
    draw_centered_text(d, "KAILALI CHAMBER", 512, 780, f_title, fill="#FFFFFF")
    f_sub = get_font(F_SANS_BOLD, 32)
    draw_centered_text(d, "COMMERCE & INDUSTRY", 512, 846, f_sub, fill="#FDE047")
    return img.resize((512, 512), Image.Resampling.LANCZOS)


def make_kanchanpur_partner_logo():
    img, d = draw_badge_base("#064E3B", "#34D399", "#A7F3D0")
    cx, cy = 512, 420
    # Grassland circle
    d.ellipse([cx - 200, cy - 200, cx + 200, cy + 200], fill="#065F46", outline="#34D399", width=6)
    # Antlers of Swamp Deer (Barasingha)
    # Left antler
    d.line([(cx - 30, cy + 80), (cx - 70, cy - 60), (cx - 130, cy - 140)], fill="#FDE047", width=12)
    d.line([(cx - 70, cy - 60), (cx - 110, cy - 80)], fill="#FDE047", width=10)
    d.line([(cx - 90, cy - 100), (cx - 70, cy - 140)], fill="#FDE047", width=10)
    # Right antler
    d.line([(cx + 30, cy + 80), (cx + 70, cy - 60), (cx + 130, cy - 140)], fill="#FDE047", width=12)
    d.line([(cx + 70, cy - 60), (cx + 110, cy - 80)], fill="#FDE047", width=10)
    d.line([(cx + 90, cy - 100), (cx + 70, cy - 140)], fill="#FDE047", width=10)
    # Reeds / wetland grass
    d.line([(cx - 140, cy + 120), (cx - 120, cy + 40)], fill="#34D399", width=6)
    d.line([(cx + 140, cy + 120), (cx + 120, cy + 40)], fill="#34D399", width=6)

    f_title = get_font(F_SANS_BOLD, 44)
    draw_centered_text(d, "SHUKLAPHANTA TRUST", 512, 780, f_title, fill="#FFFFFF")
    f_sub = get_font(F_SANS_BOLD, 32)
    draw_centered_text(d, "WILDLIFE CONSERVATION", 512, 846, f_sub, fill="#34D399")
    return img.resize((512, 512), Image.Resampling.LANCZOS)


def make_dadeldhura_partner_logo():
    img, d = draw_badge_base("#7F1D1D", "#F59E0B", "#FEF08A")
    cx, cy = 512, 420
    # Sacred temple pagoda arch
    d.polygon([(cx, cy - 170), (cx - 160, cy + 10), (cx + 160, cy + 10)], fill="#B91C1C", outline="#F59E0B", width=6)
    d.polygon([(cx, cy - 100), (cx - 190, cy + 90), (cx + 190, cy + 90)], fill="#991B1B", outline="#F59E0B", width=6)
    # Sacred golden Kalash / pinnacle
    d.ellipse([cx - 20, cy - 200, cx + 20, cy - 160], fill="#FDE047")
    d.line([(cx, cy - 220), (cx, cy - 200)], fill="#FDE047", width=6)
    # Sacred Bell
    d.chord([cx - 50, cy + 10, cx + 50, cy + 110], 0, 180, fill="#F59E0B", outline="#FEF08A", width=4)

    f_title = get_font(F_SANS_BOLD, 44)
    draw_centered_text(d, "UGRATARA HERITAGE", 512, 780, f_title, fill="#FFFFFF")
    f_sub = get_font(F_SANS_BOLD, 32)
    draw_centered_text(d, "DADELDHURA TOURISM", 512, 846, f_sub, fill="#FDE047")
    return img.resize((512, 512), Image.Resampling.LANCZOS)


def make_baitadi_partner_logo():
    img, d = draw_badge_base("#4C1D95", "#F59E0B", "#DDD6FE")
    cx, cy = 512, 420
    # Sacred Diya (Oil lamp) with eternal flame
    d.ellipse([cx - 170, cy - 40, cx + 170, cy + 110], fill="#6D28D9", outline="#F59E0B", width=6)
    # Flame
    d.polygon([(cx, cy - 170), (cx - 60, cy - 40), (cx + 60, cy - 40)], fill="#F97316")
    d.polygon([(cx, cy - 140), (cx - 35, cy - 40), (cx + 35, cy - 40)], fill="#FDE047")
    # Base pedestal
    d.rectangle([cx - 100, cy + 90, cx + 100, cy + 130], fill="#F59E0B")

    f_title = get_font(F_SANS_BOLD, 42)
    draw_centered_text(d, "TRIPURASUNDARI FORUM", 512, 780, f_title, fill="#FFFFFF")
    f_sub = get_font(F_SANS_BOLD, 32)
    draw_centered_text(d, "BAITADI HERITAGE", 512, 846, f_sub, fill="#FDE047")
    return img.resize((512, 512), Image.Resampling.LANCZOS)


def make_doti_partner_logo():
    img, d = draw_badge_base("#431407", "#FB923C", "#FED7AA")
    cx, cy = 512, 420
    # Historic citadel fortress & scroll
    # Fortress wall
    d.rectangle([cx - 160, cy - 20, cx + 160, cy + 110], fill="#7C2D12", outline="#FB923C", width=6)
    # Battlements
    for bx in range(cx - 160, cx + 160, 60):
        d.rectangle([bx, cy - 60, bx + 40, cy - 20], fill="#7C2D12", outline="#FB923C", width=4)
    # Historic quill
    d.line([(cx - 70, cy + 40), (cx + 90, cy - 140)], fill="#FED7AA", width=10)
    d.line([(cx + 90, cy - 140), (cx + 120, cy - 170)], fill="#FB923C", width=14)

    f_title = get_font(F_SANS_BOLD, 44)
    draw_centered_text(d, "SILGADHI ARCHIVES", 512, 780, f_title, fill="#FFFFFF")
    f_sub = get_font(F_SANS_BOLD, 32)
    draw_centered_text(d, "HISTORICAL SOCIETY • DOTI", 512, 846, f_sub, fill="#FB923C")
    return img.resize((512, 512), Image.Resampling.LANCZOS)


def make_achham_partner_logo():
    img, d = draw_badge_base("#134E4A", "#2DD4BF", "#99F6E4")
    cx, cy = 512, 420
    # Healing Ayurveda Lotus & River waves
    # Lotus petals
    d.polygon([(cx, cy - 160), (cx - 70, cy + 20), (cx + 70, cy + 20)], fill="#14B8A6")
    d.polygon([(cx - 40, cy - 120), (cx - 140, cy + 20), (cx, cy + 20)], fill="#0D9488")
    d.polygon([(cx + 40, cy - 120), (cx + 140, cy + 20), (cx, cy + 20)], fill="#0D9488")
    # Sacred river confluence waves
    for r_wave in (cy + 50, cy + 85, cy + 120):
        d.arc([cx - 180, r_wave - 20, cx - 20, r_wave + 20], 0, 180, fill="#2DD4BF", width=6)
        d.arc([cx - 20, r_wave - 20, cx + 140, r_wave + 20], 180, 360, fill="#2DD4BF", width=6)

    f_title = get_font(F_SANS_BOLD, 42)
    draw_centered_text(d, "VAIDYANATH TRUST", 512, 780, f_title, fill="#FFFFFF")
    f_sub = get_font(F_SANS_BOLD, 32)
    draw_centered_text(d, "ACHHAM HERITAGE", 512, 846, f_sub, fill="#2DD4BF")
    return img.resize((512, 512), Image.Resampling.LANCZOS)


def make_bajura_partner_logo():
    img, d = draw_badge_base("#0C4A6E", "#38BDF8", "#BAE6FD")
    cx, cy = 512, 420
    # Badimalika Alpine Plateau & temple
    d.polygon([(cx - 220, cy + 120), (cx, cy - 140), (cx + 220, cy + 120)], fill="#0284C7")
    d.polygon([(cx, cy - 140), (cx - 80, cy - 20), (cx + 80, cy - 20)], fill="#FFFFFF")
    # Alpine green meadow curve
    d.chord([cx - 200, cy - 20, cx + 200, cy + 130], 0, 180, fill="#16A34A")

    f_title = get_font(F_SANS_BOLD, 42)
    draw_centered_text(d, "BADIMALIKA FORUM", 512, 780, f_title, fill="#FFFFFF")
    f_sub = get_font(F_SANS_BOLD, 32)
    draw_centered_text(d, "BAJURA ALPINE CONSERVATION", 512, 846, f_sub, fill="#38BDF8")
    return img.resize((512, 512), Image.Resampling.LANCZOS)


def make_bajhang_partner_logo():
    img, d = draw_badge_base("#0F172A", "#06B6D4", "#67E8F9")
    cx, cy = 512, 420
    # Mount Saipal towering peak & climbing axe
    d.polygon([(cx - 240, cy + 120), (cx, cy - 190), (cx + 240, cy + 120)], fill="#1E293B", outline="#06B6D4", width=4)
    # Snow face
    d.polygon([(cx, cy - 190), (cx - 100, cy - 50), (cx - 20, cy + 40), (cx, cy - 10), (cx + 30, cy + 30), (cx + 120, cy - 50)], fill="#FFFFFF")
    # Crossed climbing axe
    d.line([(cx - 120, cy + 90), (cx + 120, cy - 80)], fill="#06B6D4", width=8)
    d.polygon([(cx + 100, cy - 100), (cx + 140, cy - 80), (cx + 120, cy - 60)], fill="#F59E0B")

    f_title = get_font(F_SANS_BOLD, 42)
    draw_centered_text(d, "SAIPAL EXPEDITION", 512, 780, f_title, fill="#FFFFFF")
    f_sub = get_font(F_SANS_BOLD, 32)
    draw_centered_text(d, "BAJHANG MOUNTAIN CLUB", 512, 846, f_sub, fill="#06B6D4")
    return img.resize((512, 512), Image.Resampling.LANCZOS)


def make_darchula_partner_logo():
    img, d = draw_badge_base("#1E1B4B", "#818CF8", "#C7D2FE")
    cx, cy = 512, 420
    # Api Peak & Trans-Himalayan floral emblem
    d.polygon([(cx - 230, cy + 110), (cx - 20, cy - 180), (cx + 190, cy + 110)], fill="#312E81", outline="#818CF8", width=4)
    d.polygon([(cx - 20, cy - 180), (cx - 90, cy - 40), (cx + 60, cy - 30)], fill="#FFFFFF")
    # Nampa secondary peak
    d.polygon([(cx + 30, cy + 110), (cx + 130, cy - 110), (cx + 250, cy + 110)], fill="#4338CA")
    d.polygon([(cx + 130, cy - 110), (cx + 90, cy - 10), (cx + 170, cy - 10)], fill="#FFFFFF")

    f_title = get_font(F_SANS_BOLD, 42)
    draw_centered_text(d, "API NAMPA COUNCIL", 512, 780, f_title, fill="#FFFFFF")
    f_sub = get_font(F_SANS_BOLD, 32)
    draw_centered_text(d, "DARCHULA CONSERVATION", 512, 846, f_sub, fill="#818CF8")
    return img.resize((512, 512), Image.Resampling.LANCZOS)


DISTRICT_PARTNERS = [
    {
        "slug": "kailali",
        "name_en": "Kailali Chamber of Commerce & Industry",
        "name_ne": "कैलाली उद्योग वाणिज्य संघ",
        "role_en": "REGIONAL TRADE & COMMERCE",
        "role_ne": "व्यापार तथा उद्योग प्रवर्द्धन",
        "url": "https://kailalichamber.org.np",
        "filename": "partner_kailali.png",
        "gen_fn": make_kailali_partner_logo,
    },
    {
        "slug": "kanchanpur",
        "name_en": "Shuklaphanta Nature & Wildlife Trust",
        "name_ne": "शुक्लाफाँटा प्रकृति तथा वन्यजन्तु संरक्षण प्रतिष्ठान",
        "role_en": "WILDLIFE CONSERVATION",
        "role_ne": "वन्यजन्तु तथा सिमसार संरक्षण",
        "url": "https://shuklaphanta.org.np",
        "filename": "partner_kanchanpur.png",
        "gen_fn": make_kanchanpur_partner_logo,
    },
    {
        "slug": "dadeldhura",
        "name_en": "Ugratara Heritage & Tourism Council",
        "name_ne": "उग्रतारा सम्पदा तथा पर्यटन विकास परिषद",
        "role_en": "HERITAGE CONSERVATION",
        "role_ne": "धार्मिक सम्पदा तथा पर्यटन",
        "url": "https://ugrataraheritage.org.np",
        "filename": "partner_dadeldhura.png",
        "gen_fn": make_dadeldhura_partner_logo,
    },
    {
        "slug": "baitadi",
        "name_en": "Tripurasundari Cultural & Social Forum",
        "name_ne": "त्रिपुरासुन्दरी सांस्कृतिक तथा सामाजिक मञ्च",
        "role_en": "COMMUNITY HERITAGE",
        "role_ne": "सांस्कृतिक संरक्षण तथा सहकार्य",
        "url": "https://tripurasundari.org.np",
        "filename": "partner_baitadi.png",
        "gen_fn": make_baitadi_partner_logo,
    },
    {
        "slug": "doti",
        "name_en": "Silgadhi Historical Research Society",
        "name_ne": "सिलगढी ऐतिहासिक तथा अनुसन्धान समाज",
        "role_en": "HISTORICAL ARCHIVES",
        "role_ne": "ऐतिहासिक अध्ययन तथा अनुसन्धान",
        "url": "https://silgadhihistory.org.np",
        "filename": "partner_doti.png",
        "gen_fn": make_doti_partner_logo,
    },
    {
        "slug": "achham",
        "name_en": "Vaidyanath Kshetra Development Trust",
        "name_ne": "वैद्यनाथ क्षेत्र विकास कोष",
        "role_en": "AYURVEDA & PILGRIMAGE",
        "role_ne": "आयुर्वेद तथा तीर्थस्थल विकास",
        "url": "https://vaidyanath.org.np",
        "filename": "partner_achham.png",
        "gen_fn": make_achham_partner_logo,
    },
    {
        "slug": "bajura",
        "name_en": "Badimalika Conservation Forum",
        "name_ne": "बडिमालिका संरक्षण तथा पर्यावरण समाज",
        "role_en": "ALPINE ECO-TOURISM",
        "role_ne": "हिमाल तथा जैविक विविधता",
        "url": "https://badimalika.org.np",
        "filename": "partner_bajura.png",
        "gen_fn": make_bajura_partner_logo,
    },
    {
        "slug": "bajhang",
        "name_en": "Saipal Himalayan Expedition Club",
        "name_ne": "सैपाल हिमाल आरोहण तथा साहसिक पर्यटन प्रतिष्ठान",
        "role_en": "MOUNTAIN ADVENTURE",
        "role_ne": "साहसिक पर्यटन तथा पर्वतारोहण",
        "url": "https://saipaladventure.org.np",
        "filename": "partner_bajhang.png",
        "gen_fn": make_bajhang_partner_logo,
    },
    {
        "slug": "darchula",
        "name_en": "Api Nampa Conservation & Biodiversity Council",
        "name_ne": "अपि नाम्पा संरक्षण तथा जैविक विविधता परिषद",
        "role_en": "TRANS-HIMALAYAN ECOLOGY",
        "role_ne": "संरक्षित क्षेत्र तथा जैविक विविधता",
        "url": "https://apinampa.org.np",
        "filename": "partner_darchula.png",
        "gen_fn": make_darchula_partner_logo,
    },
]


class Command(BaseCommand):
    help = "Generates high quality logos for all 9 district partners and links them to districts."

    def handle(self, *args, **options):
        partners_dir = os.path.join(settings.MEDIA_ROOT, "partners")
        os.makedirs(partners_dir, exist_ok=True)

        for item in DISTRICT_PARTNERS:
            district = District.objects.filter(slug=item["slug"]).first()
            if not district:
                self.stdout.write(self.style.WARNING(f"District {item['slug']} not found!"))
                continue

            filepath = os.path.join(partners_dir, item["filename"])
            img = item["gen_fn"]()
            img.save(filepath, "PNG")
            self.stdout.write(f"Generated district logo: {filepath}")

            rel_path = f"partners/{item['filename']}"

            partner, created = Partner.objects.update_or_create(
                district=district,
                defaults={
                    "name": item["name_en"],
                    "name_en": item["name_en"],
                    "name_ne": item["name_ne"],
                    "role": item["role_en"],
                    "role_en": item["role_en"],
                    "role_ne": item["role_ne"],
                    "image": rel_path,
                    "url": item["url"],
                }
            )

            status = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"{status} Partner for District '{district.name}' (#{partner.id}: {partner.name}) -> {rel_path}"))

        self.stdout.write(self.style.SUCCESS("All 9 district partners successfully created and linked!"))
