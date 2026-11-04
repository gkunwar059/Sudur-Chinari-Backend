from django.core.management.base import BaseCommand
from apps.articles.models import HeroSlide, Article

class Command(BaseCommand):
    help = 'Seeds initial curated hero slides for Sudurpashchim Digital broadsheet hero section'

    def handle(self, *args, **options):
        # 1. Slide 1: Achham / Identity
        s1, created = HeroSlide.objects.get_or_create(
            order=1,
            defaults={
                'title_ne': "हाम्रो कथा, हाम्रो पहिचान।",
                'title_en': "Our Story, Our Identity.",
                'subtitle_ne': "परिचय",
                'subtitle_en': "Identity",
                'excerpt_ne': "अछामका इतिहास, कला, संस्कृति र लोकजीवनका कथा, सम्झना र सीपहरूलाई एउटै खुला संग्रहमा जोड्दैछौं। तपाईको कथा पनि यहाँ जोड्नुहोस्।",
                'excerpt_en': "Connecting the history, art, culture, and folk stories of Achham into a single open archive. Share and preserve your voice here.",
                'image_url': "/images/karnali_bridge.jpg",
                'primary_button_text_ne': "कथा खोज्नुहोस्",
                'primary_button_text_en': "Explore Stories",
                'primary_button_url': "/district",
                'secondary_button_text_ne': "आफ्नो कथा राख्नुहोस्",
                'secondary_button_text_en': "Share Your Story",
                'secondary_button_url': "",
                'is_active': True,
            }
        )
        if not created:
            s1.title_ne = "हाम्रो कथा, हाम्रो पहिचान।"
            s1.title_en = "Our Story, Our Identity."
            s1.subtitle_ne = "परिचय"
            s1.subtitle_en = "Identity"
            s1.excerpt_ne = "अछामका इतिहास, कला, संस्कृति र लोकजीवनका कथा, सम्झना र सीपहरूलाई एउटै खुला संग्रहमा जोड्दैछौं। तपाईको कथा पनि यहाँ जोड्नुहोस्।"
            s1.excerpt_en = "Connecting the history, art, culture, and folk stories of Achham into a single open archive. Share and preserve your voice here."
            s1.image_url = "/images/karnali_bridge.jpg"
            s1.primary_button_text_ne = "कथा खोज्नुहोस्"
            s1.primary_button_text_en = "Explore Stories"
            s1.primary_button_url = "/district"
            s1.secondary_button_text_ne = "आफ्नो कथा राख्नुहोस्"
            s1.secondary_button_text_en = "Share Your Story"
            s1.is_active = True
            s1.save()

        # 2. Slide 2: Badimalika Pilgrimage
        s2, created = HeroSlide.objects.get_or_create(
            order=2,
            defaults={
                'title_ne': "बडिमालिकाको आध्यात्मिक यात्रा",
                'title_en': "Spiritual Journey to Badimalika",
                'subtitle_ne': "तीर्थयात्रा",
                'subtitle_en': "Pilgrimage",
                'excerpt_ne': "अद्भुत हिमाली फाँटहरूका बीच अवस्थित सबैभन्दा पूज्य हिन्दू मन्दिरहरूको पवित्र तीर्थयात्रा गर्नुहोस् र प्राकृतिक सौन्दर्यको अवलोकन गर्नुहोस्।",
                'excerpt_en': "Embark on a sacred pilgrimage to one of the most revered alpine temples set amidst breathtaking high-altitude meadows.",
                'image_url': "/images/places/baidyanath_achham.jpg",
                'primary_button_text_ne': "कथा खोज्नुहोस्",
                'primary_button_text_en': "Find Stories",
                'primary_button_url': "/district",
                'secondary_button_text_ne': "आफ्नो कथा राख्नुहोस्",
                'secondary_button_text_en': "Share Your Story",
                'secondary_button_url': "",
                'is_active': True,
            }
        )
        if not created:
            s2.title_ne = "बडिमालिकाको आध्यात्मिक यात्रा"
            s2.title_en = "Spiritual Journey to Badimalika"
            s2.subtitle_ne = "तीर्थयात्रा"
            s2.subtitle_en = "Pilgrimage"
            s2.excerpt_ne = "अद्भुत हिमाली फाँटहरूका बीच अवस्थित सबैभन्दा पूज्य हिन्दू मन्दिरहरूको पवित्र तीर्थयात्रा गर्नुहोस् र प्राकृतिक सौन्दर्यको अवलोकन गर्नुहोस्।"
            s2.excerpt_en = "Embark on a sacred pilgrimage to one of the most revered alpine temples set amidst breathtaking high-altitude meadows."
            s2.image_url = "/images/places/baidyanath_achham.jpg"
            s2.primary_button_text_ne = "कथा खोज्नुहोस्"
            s2.primary_button_text_en = "Find Stories"
            s2.primary_button_url = "/district"
            s2.secondary_button_text_ne = "आफ्नो कथा राख्नुहोस्"
            s2.secondary_button_text_en = "Share Your Story"
            s2.is_active = True
            s2.save()

        # 3. Slide 3: Shuklaphanta National Park
        s3, created = HeroSlide.objects.get_or_create(
            order=3,
            defaults={
                'title_ne': "शुक्लाफाँटा राष्ट्रिय निकुञ्ज",
                'title_en': "Untamed Shuklaphanta National Park",
                'subtitle_ne': "वन्यजन्तु",
                'subtitle_en': "Wildlife",
                'excerpt_ne': "वन्यजन्तु सफारीको रोमाञ्चकता अनुभव गर्नुहोस् र एसियाकै सबैभन्दा ठूलो बाह्रसिंगेको बथान तथा दुर्लभ वन्यजन्तुको अवलोकन गर्नुहोस्।",
                'excerpt_en': "Experience the thrill of wildlife safaris and witness the largest herd of swamp deer in Asia along with rare biodiversity.",
                'image_url': "/images/places/khaptad_national_park.jpg",
                'primary_button_text_ne': "कथा खोज्नुहोस्",
                'primary_button_text_en': "Find Stories",
                'primary_button_url': "/district",
                'secondary_button_text_ne': "आफ्नो कथा राख्नुहोस्",
                'secondary_button_text_en': "Share Your Story",
                'secondary_button_url': "",
                'is_active': True,
            }
        )
        if not created:
            s3.title_ne = "शुक्लाफाँटा राष्ट्रिय निकुञ्ज"
            s3.title_en = "Untamed Shuklaphanta National Park"
            s3.subtitle_ne = "वन्यजन्तु"
            s3.subtitle_en = "Wildlife"
            s3.excerpt_ne = "वन्यजन्तु सफारीको रोमाञ्चकता अनुभव गर्नुहोस् र एसियाकै सबैभन्दा ठूलो बाह्रसिंगेको बथान तथा दुर्लभ वन्यजन्तुको अवलोकन गर्नुहोस्।"
            s3.excerpt_en = "Experience the thrill of wildlife safaris and witness the largest herd of swamp deer in Asia along with rare biodiversity."
            s3.image_url = "/images/places/khaptad_national_park.jpg"
            s3.primary_button_text_ne = "कथा खोज्नुहोस्"
            s3.primary_button_text_en = "Find Stories"
            s3.primary_button_url = "/district"
            s3.secondary_button_text_ne = "आफ्नो कथा राख्नुहोस्"
            s3.secondary_button_text_en = "Share Your Story"
            s3.is_active = True
            s3.save()

        self.stdout.write(self.style.SUCCESS('Successfully seeded 3 Hero Slides!'))
