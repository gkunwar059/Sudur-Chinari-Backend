from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.ads.models import BannerAd
from apps.common.models import TrendingTopic
from apps.districts.models import District
from apps.products.models import ProductCategory, LocalProduct, ProductProducer
from apps.yatayat.models import TransportService, TransportLocation, EmergencyHelpline
from apps.multimedia.models import VideoItem, PhotoStory, PhotoStoryImage

class Command(BaseCommand):
    help = "Seeds initial data for newly created models (BannerAd, Products, Yatayat, Trending Topics, Helplines)"

    def handle(self, *args, **options):
        self.stdout.write("Seeding Banner Ads...")
        self.seed_banner_ads()

        self.stdout.write("Seeding Trending Topics...")
        self.seed_trending_topics()

        self.stdout.write("Seeding Local Products & Producers...")
        self.seed_products()

        self.stdout.write("Seeding Yatayat Services & Locations...")
        self.seed_yatayat()

        self.stdout.write("Seeding Emergency Helplines...")
        self.seed_helplines()

        self.stdout.write("Seeding Photo Story Images...")
        self.seed_photo_story_images()

        self.stdout.write(self.style.SUCCESS("Successfully seeded all new APIs data!"))

    def seed_banner_ads(self):
        ads = [
            {
                "placement": "top-leaderboard",
                "title": "Nepal Telecom 5G Network",
                "image_url": "/images/ads/telecom_5g_banner.jpg",
                "target_url": "https://ntc.net.np",
                "alt_text": "Nepal Telecom 5G Network - Experience the Future Now",
                "advertiser": "Nepal Telecom",
            },
            {
                "placement": "billboard-mid",
                "title": "Visit Khaptad & Sudurpashchim Nepal 2026",
                "image_url": "/images/ads/tourism_banner.jpg",
                "target_url": "/category/tourism",
                "alt_text": "Visit Khaptad & Sudurpashchim Nepal 2026 - Discover the Unexplored",
                "advertiser": "Nepal Tourism Board",
            },
            {
                "placement": "sidebar",
                "title": "Rastriya Banijya Bank - Agri Loans",
                "image_url": "/images/ads/bank_sidebar_ad.jpg",
                "target_url": "/category/economy",
                "alt_text": "Rastriya Banijya Bank - Sudurpashchim Agri & Business Loans",
                "advertiser": "Rastriya Banijya Bank",
            },
            {
                "placement": "in-article",
                "title": "Far-Western University Admissions 2026",
                "image_url": "/images/ads/university_banner.jpg",
                "target_url": "/category/education",
                "alt_text": "Far-Western University Admissions Open 2026",
                "advertiser": "Far-Western University",
            },
            {
                "placement": "bottom-strip",
                "title": "Far-Western University Higher Education",
                "image_url": "/images/ads/university_banner.jpg",
                "target_url": "/category/education",
                "alt_text": "Far-Western University - Excellence in Higher Education",
                "advertiser": "Far-Western University",
            },
        ]
        for ad_data in ads:
            BannerAd.objects.update_or_create(
                placement=ad_data["placement"],
                defaults=ad_data
            )

    def seed_trending_topics(self):
        topics = [
            ("कर्णाली पुल", "karnali-bridge", 450, 1),
            ("खप्तड पर्यटन", "khaptad-tourism", 380, 2),
            ("प्रदेश बजेट", "provincial-budget", 320, 3),
            ("सेती अस्पताल", "seti-hospital", 290, 4),
            ("देउडा संस्कृति", "deuda-culture", 260, 5),
            ("दोधारा चाँदनी", "dodhara-chandani", 240, 6),
            ("शुक्लाफाँटा", "shuklaphanta", 210, 7),
        ]
        for name_ne, slug, count, order in topics:
            TrendingTopic.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name_ne,
                    "name_ne": name_ne,
                    "name_en": slug.replace('-', ' ').title(),
                    "search_count": count,
                    "order": order,
                    "is_active": True,
                }
            )

    def seed_products(self):
        cats = [
            ("dairy", "दुग्धजन्य", "Dairy", "🥛", 1),
            ("grains", "अन्न/धान्य", "Grains", "🌾", 2),
            ("fruits", "फलफूल", "Fruits", "🍎", 3),
            ("spices", "मसला/जडीबुटी", "Spices", "🌿", 4),
        ]
        cat_objs = {}
        for slug, name_ne, name_en, icon, order in cats:
            obj, _ = ProductCategory.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name_en,
                    "name_en": name_en,
                    "name_ne": name_ne,
                    "icon": icon,
                    "order": order,
                    "is_active": True,
                }
            )
            cat_objs[slug] = obj

        achham = District.objects.filter(slug="achham").first()
        kailali = District.objects.filter(slug="kailali").first()
        darchula = District.objects.filter(slug="darchula").first()
        dist = achham or kailali or District.objects.first()

        if dist and "dairy" in cat_objs:
            ghee, _ = LocalProduct.objects.update_or_create(
                slug="ghee",
                defaults={
                    "name": "Pure Local Ghee",
                    "name_en": "Pure Local Ghee",
                    "name_ne": "शुद्ध स्थानीय घ्यू",
                    "category": cat_objs["dairy"],
                    "district": dist,
                    "description": "Pure local cow and buffalo ghee from high pasture regions.",
                    "description_en": "Pure local cow and buffalo ghee from high pasture regions.",
                    "description_ne": "स्थानीय गाई/भैंसीको शुद्ध प्राकृतिक घ्यू।",
                    "image_url": "https://images.unsplash.com/photo-1588195538326-c5b1e9f80a1b?q=80&w=600&auto=format&fit=crop",
                    "estimated_price_range": "Rs. 800 - 850 / kg",
                    "unit": "kg",
                    "is_featured": True,
                }
            )

            milk, _ = LocalProduct.objects.update_or_create(
                slug="local-milk",
                defaults={
                    "name": "Organic Fresh Milk",
                    "name_en": "Organic Fresh Milk",
                    "name_ne": "ताजा अर्गानिक दुध",
                    "category": cat_objs["dairy"],
                    "district": dist,
                    "description": "Fresh morning cow milk delivered directly from local dairy farms.",
                    "description_en": "Fresh morning cow milk delivered directly from local dairy farms.",
                    "description_ne": "स्थानीय डेरी फार्मबाट संकलित ताजा गाईको दुध।",
                    "image_url": "https://images.unsplash.com/photo-1550583724-b2692b85b150?q=80&w=600&auto=format&fit=crop",
                    "estimated_price_range": "Rs. 90 - 110 / litre",
                    "unit": "litre",
                    "is_featured": False,
                }
            )

            # Seed Producers
            f1, _ = ProductProducer.objects.update_or_create(
                name="Dhan Bahadur Kunwar",
                district=dist,
                defaults={
                    "name_en": "Dhan Bahadur Kunwar",
                    "name_ne": "धन बहादुर कुँवर",
                    "municipality_address": "Sanfebagar - 3, Achham",
                    "municipality_address_en": "Sanfebagar - 3, Achham",
                    "municipality_address_ne": "साँफेबगर - ३, अछाम",
                    "phone": "9848712345",
                    "experience_years": "12 Years",
                    "avatar_url": "https://images.unsplash.com/photo-1542838132-92c53300491e?q=80&w=300&auto=format&fit=crop",
                    "is_verified": True,
                }
            )
            f1.products.add(ghee)

            f2, _ = ProductProducer.objects.update_or_create(
                name="Kamala Devi Khadka",
                district=dist,
                defaults={
                    "name_en": "Kamala Devi Khadka",
                    "name_ne": "कमला देवी खड्का",
                    "municipality_address": "Chaurpati - 6, Achham",
                    "municipality_address_en": "Chaurpati - 6, Achham",
                    "municipality_address_ne": "चौरपाटी - ६, अछाम",
                    "phone": "9868754321",
                    "experience_years": "8 Years",
                    "avatar_url": "https://images.unsplash.com/photo-1559583985-c80d8ad9b29f?q=80&w=300&auto=format&fit=crop",
                    "is_verified": True,
                }
            )
            f2.products.add(ghee, milk)

        if darchula and "spices" in cat_objs:
            LocalProduct.objects.update_or_create(
                slug="yarsagumba-herbs",
                defaults={
                    "name": "High Mountain Himalayan Herbs",
                    "name_en": "High Mountain Himalayan Herbs",
                    "name_ne": "उच्च हिमाली जडीबुटी तथा यार्सागुम्बा",
                    "category": cat_objs["spices"],
                    "district": darchula,
                    "description": "Authentic herbs and medicinal plants gathered from Byas and Api Nampa region.",
                    "description_en": "Authentic herbs and medicinal plants gathered from Byas and Api Nampa region.",
                    "description_ne": "व्यास तथा अपि नाम्पा क्षेत्रबाट संकलित प्रामाणिक हिमाली जडीबुटी।",
                    "image_url": "https://images.unsplash.com/photo-1509358271058-acd22cc93898?q=80&w=600&auto=format&fit=crop",
                    "estimated_price_range": "Market Rate",
                    "unit": "packet",
                    "is_featured": True,
                }
            )

    def seed_yatayat(self):
        kailali = District.objects.filter(slug="kailali").first()
        kanchanpur = District.objects.filter(slug="kanchanpur").first()
        achham = District.objects.filter(slug="achham").first()

        # Seed Locations
        hubs = [
            ("Dhangadhi Central Bus Park", "धनगढी केन्द्रीय बसपार्क", kailali, True, "091-521234"),
            ("Mahendranagar Bus Park", "महेन्द्रनगर बसपार्क", kanchanpur, True, "099-521122"),
            ("Attariya Central Junction", "अत्तरिया केन्द्रीय चोक", kailali, True, "091-550111"),
            ("Sanfebagar Bus Counter", "साँफेबगर बस काउन्टर", achham, False, "097-620111"),
        ]
        for name_en, name_ne, dist, is_hub, phone in hubs:
            if dist:
                TransportLocation.objects.update_or_create(
                    name=name_en,
                    defaults={
                        "name_en": name_en,
                        "name_ne": name_ne,
                        "district": dist,
                        "is_hub": is_hub,
                        "phone": phone,
                        "helpdesk_contact": "103",
                    }
                )

        # Seed Services
        services = [
            {
                "title": "Achham Yatayat Pvt. Ltd.",
                "title_en": "Achham Yatayat Pvt. Ltd.",
                "title_ne": "अछाम यातायात प्रा.लि.",
                "sub_title": "Super Deluxe AC Bus Service",
                "sub_title_en": "Super Deluxe AC Bus Service",
                "sub_title_ne": "सुपर्डीलक्स बस सेवा",
                "service_type": "bus",
                "badge_text": "Popular",
                "badge_text_en": "Popular",
                "badge_text_ne": "लोकप्रिय",
                "badge_color": "emerald",
                "origin_name": "Sanfebagar",
                "origin_name_en": "Sanfebagar",
                "origin_name_ne": "साँफेबगर",
                "destination_name": "Dhangadhi",
                "destination_name_en": "Dhangadhi",
                "destination_name_ne": "धनगढी",
                "route_stops": ["Sanfebagar", "Bayalpata", "Dipayal", "Attariya", "Dhangadhi"],
                "departure_time": "6:00 AM",
                "departure_time_en": "6:00 AM",
                "departure_time_ne": "बिहान ६:०० बजे",
                "estimated_fare": "Rs. 1,200",
                "estimated_fare_en": "Rs. 1,200",
                "estimated_fare_ne": "रु. १,२००",
                "total_seats": "36",
                "contact_numbers": ["98580-12345", "98487-67890"],
                "image_url": "/images/yatayat/bus_achham.jpg",
                "notes": "Air-conditioned (AC), comfortable pushback seats, free Wi-Fi and water bottles.",
                "notes_en": "Air-conditioned (AC), comfortable pushback seats, free Wi-Fi and water bottles.",
                "notes_ne": "वातानुकूलित (AC), आरामदायी सिट, निःशुल्क वाइफाइ तथा पानीको सुविधा उपलब्ध।",
                "verified": True,
            },
            {
                "title": "Dolphin Yatayat Service",
                "title_en": "Dolphin Yatayat Service",
                "title_ne": "डल्फिन यातायात सेवा",
                "sub_title": "AC Sleeper / Super Deluxe",
                "sub_title_en": "AC Sleeper / Super Deluxe",
                "sub_title_ne": "एसी स्लीपर/सुपर्डीलक्स",
                "service_type": "bus",
                "badge_text": "Daily Service",
                "badge_text_en": "Daily Service",
                "badge_text_ne": "नियमित सेवा",
                "badge_color": "blue",
                "origin_name": "Dhangadhi",
                "origin_name_en": "Dhangadhi",
                "origin_name_ne": "धनगढी",
                "destination_name": "Sanfebagar",
                "destination_name_en": "Sanfebagar",
                "destination_name_ne": "साँफेबगर",
                "route_stops": ["Dhangadhi", "Attariya", "Dipayal", "Bayalpata", "Sanfebagar"],
                "departure_time": "7:00 AM",
                "departure_time_en": "7:00 AM",
                "departure_time_ne": "बिहान ७:०० बजे",
                "estimated_fare": "Rs. 1,000",
                "estimated_fare_en": "Rs. 1,000",
                "estimated_fare_ne": "रु. १,०००",
                "total_seats": "40",
                "contact_numbers": ["98574-11223", "97483-44556"],
                "image_url": "/images/yatayat/bus_dolphin.jpg",
                "notes": "Modern sleeper coach, mobile USB charging ports, veteran mountain drivers.",
                "notes_en": "Modern sleeper coach, mobile USB charging ports, veteran mountain drivers.",
                "notes_ne": "आधुनिक स्लीपर कोच, मोबाइल चार्जिङ पोर्ट, अनुभवी चालक तथा सुरक्षित यात्रा।",
                "verified": True,
            },
            {
                "title": "Mahendranagar Express Hiace",
                "title_en": "Mahendranagar Express Hiace",
                "title_ne": "महेन्द्रनगर एक्सप्रेस हाइस",
                "sub_title": "Fast Mountain Hiace",
                "sub_title_en": "Fast Mountain Hiace",
                "sub_title_ne": "छिटो र सुरक्षित यात्रा",
                "service_type": "hiace",
                "badge_text": "Fast Transit",
                "badge_text_en": "Fast Transit",
                "badge_text_ne": "द्रुत सेवा",
                "badge_color": "brand",
                "origin_name": "Mahendranagar",
                "origin_name_en": "Mahendranagar",
                "origin_name_ne": "महेन्द्रनगर",
                "destination_name": "Dipayal",
                "destination_name_en": "Dipayal",
                "destination_name_ne": "दिपायल",
                "route_stops": ["Mahendranagar", "Attariya", "Bhimdatta", "Dipayal"],
                "departure_time": "8:30 AM",
                "departure_time_en": "8:30 AM",
                "departure_time_ne": "बिहान ८:३० बजे",
                "estimated_fare": "Rs. 850",
                "estimated_fare_en": "Rs. 850",
                "estimated_fare_ne": "रु. ८५०",
                "total_seats": "14",
                "contact_numbers": ["98123-45678"],
                "image_url": "/images/yatayat/hiace_mahendranagar.jpg",
                "notes": "Fast transit with limited stops, experienced hill drivers.",
                "notes_en": "Fast transit with limited stops, experienced hill drivers.",
                "notes_ne": "द्रुत सेवा, सीमित स्टपहरु, अनुभवी पहाडी चालक।",
                "verified": True,
            },
            {
                "title": "Khaptad Mountain 4WD Jeep",
                "title_en": "Khaptad Mountain 4WD Jeep",
                "title_ne": "खप्तड माउन्टेन ४WD जीप",
                "sub_title": "All-Terrain Offroad Jeep",
                "sub_title_en": "All-Terrain Offroad Jeep",
                "sub_title_ne": "अफरोड जीप सेवा",
                "service_type": "jeep",
                "badge_text": "All Terrain",
                "badge_text_en": "All Terrain",
                "badge_text_ne": "अफरोड",
                "badge_color": "amber",
                "origin_name": "Dhangadhi",
                "origin_name_en": "Dhangadhi",
                "origin_name_ne": "धनगढी",
                "destination_name": "Bajura",
                "destination_name_en": "Bajura",
                "destination_name_ne": "बाजुरा",
                "route_stops": ["Dhangadhi", "Sanfebagar", "Martadi", "Bajura"],
                "departure_time": "5:30 AM",
                "departure_time_en": "5:30 AM",
                "departure_time_ne": "बिहान ५:३० बजे",
                "estimated_fare": "Rs. 2,000",
                "estimated_fare_en": "Rs. 2,000",
                "estimated_fare_ne": "रु. २,०००",
                "total_seats": "9",
                "contact_numbers": ["98687-99887"],
                "image_url": "/images/yatayat/jeep_bajura.jpg",
                "notes": "Sturdy 4WD vehicle built for tough mountain paths and adverse weather.",
                "notes_en": "Sturdy 4WD vehicle built for tough mountain paths and adverse weather.",
                "notes_ne": "कठिन पहाडी बाटो र प्रतिकूल मौसमका लागि उपयुक्त ४x४ जीप।",
                "verified": True,
            },
        ]
        for s_data in services:
            TransportService.objects.update_or_create(
                title=s_data["title"],
                service_type=s_data["service_type"],
                defaults=s_data
            )

    def seed_helplines(self):
        kailali = District.objects.filter(slug="kailali").first()
        kanchanpur = District.objects.filter(slug="kanchanpur").first()

        lines = [
            ("Nepal Traffic Police Helpline", "नेपाल ट्राफिक प्रहरी हेल्पलाइन", "traffic", None, "103", "24/7 Toll Free", "चौबीसै घण्टा खुला", True, 1),
            ("Dhangadhi Buspark Counter", "धनगढी बसपार्क काउन्टर", "buspark", kailali, "091-521234", "Kailali", "कैलाली", False, 2),
            ("Mahendranagar Buspark Counter", "महेन्द्रनगर बसपार्क काउन्टर", "buspark", kanchanpur, "099-521122", "Kanchanpur", "कञ्चनपुर", False, 3),
            ("Attariya Junction Helpdesk", "अत्तरिया मुख्य चोक सहायता कक्ष", "helpdesk", kailali, "091-550111", "Central Junction", "केन्द्रीय जंक्सन", False, 4),
        ]
        for title_en, title_ne, cat, dist, phone, sub_en, sub_ne, is_24, order in lines:
            EmergencyHelpline.objects.update_or_create(
                phone_number=phone,
                defaults={
                    "title": title_en,
                    "title_en": title_en,
                    "title_ne": title_ne,
                    "category": cat,
                    "district": dist,
                    "subtitle": sub_en,
                    "subtitle_en": sub_en,
                    "subtitle_ne": sub_ne,
                    "is_24_7": is_24,
                    "order": order,
                }
            )

    def seed_photo_story_images(self):
        stories = PhotoStory.objects.all()
        sample_images = [
            "https://images.unsplash.com/photo-1544735716-392fe2489ffa?q=80&w=800&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?q=80&w=800&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1506744038136-46273834b3fb?q=80&w=800&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1519681393784-d120267933ba?q=80&w=800&auto=format&fit=crop",
        ]
        for story in stories:
            if not story.images.exists():
                for idx, img_url in enumerate(sample_images, 1):
                    PhotoStoryImage.objects.create(
                        story=story,
                        image_url=img_url,
                        caption=f"View of {story.title} #{idx}",
                        caption_en=f"View of {story.title} #{idx}",
                        caption_ne=f"{story.title}को दृश्य #{idx}",
                        order=idx
                    )
                story.imageCount = len(sample_images)
                story.save(update_fields=['imageCount'])
