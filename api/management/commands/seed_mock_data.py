import json
from pathlib import Path
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
from api.models import (
    Category, Author, District, Article, Tag, ArticleComment,
    DistrictTheme, DistrictStats, DistrictCulture, DistrictPlace,
    UserProfile, Amenity, Hotel, HotelRoom, HotelGallery, HotelNearbyPlace,
    PopupAd
)

User = get_user_model()
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
MOCK_FILE = BASE_DIR / "mock_data.json"

class Command(BaseCommand):
    help = "Seed database from mock_data.json, hotels, popup ads, and default admin user."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Starting database seeding...")
        
        if not MOCK_FILE.exists():
            self.stderr.write(f"mock_data.json not found at {MOCK_FILE}")
            return

        with open(MOCK_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 1. Superuser
        self.seed_superuser()

        # 2. Categories
        cat_map = self.seed_categories(data.get('categories', []))

        # 3. Authors
        author_map = self.seed_authors(data.get('authors', []))

        # 4. Districts (with themes, stats, culture, places)
        dist_map = self.seed_districts(data.get('districts', []))

        # 5. Articles (with tags)
        art_map = self.seed_articles(data.get('articles', []), cat_map, author_map, dist_map)

        # 6. Comments
        self.seed_comments(data.get('comments', {}), art_map)

        # 7. Amenities & Hotels
        self.seed_hotels(dist_map, cat_map)

        # 8. Popup Roadblock Ads
        self.seed_popup_ads()

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))

    def seed_superuser(self):
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@sudurpashchim.com',
                'first_name': 'Sudur',
                'last_name': 'Admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('admin123')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        UserProfile.objects.update_or_create(
            user=admin_user,
            defaults={'phone': '9800000000'}
        )
        self.stdout.write(f"  {'Created' if created else 'Updated'} superuser: admin / admin123")

    def seed_categories(self, categories_data):
        self.stdout.write("Seeding categories...")
        cat_map = {}
        layout_mapping = {
            'news': 'news',
            'politics': 'politics',
            'sports': 'sports',
            'tourism': 'tourism',
            'stay': 'stay',
        }

        order_idx = 10
        for cat in categories_data:
            slug = cat.get('slug')
            name_obj = cat.get('name', {})
            name_ne = name_obj.get('ne', '') if isinstance(name_obj, dict) else str(name_obj)
            name_en = name_obj.get('en', '') if isinstance(name_obj, dict) else str(name_obj)
            icon = cat.get('icon', '')
            layout_type = layout_mapping.get(slug, 'default')

            obj, created = Category.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': name_en,
                    'name_en': name_en,
                    'name_ne': name_ne,
                    'icon': icon,
                    'layout_type': layout_type,
                    'show_in_menu': True,
                    'order': order_idx,
                }
            )
            cat_map[cat.get('id')] = obj
            cat_map[slug] = obj
            order_idx += 10

        # Ensure 'stay' category exists
        stay_cat, created = Category.objects.update_or_create(
            slug='stay',
            defaults={
                'name': 'Hotels & Stay',
                'name_en': 'Hotels & Stay',
                'name_ne': 'होटल तथा बासस्थान',
                'icon': '🏨',
                'layout_type': 'stay',
                'show_in_menu': True,
                'order': 85,
            }
        )
        cat_map['stay'] = stay_cat

        self.stdout.write(f"  Seeded {Category.objects.count()} categories.")
        return cat_map

    def seed_authors(self, authors_data):
        self.stdout.write("Seeding authors...")
        author_map = {}
        for author in authors_data:
            slug = author.get('slug') or author.get('id')
            name_obj = author.get('name', {})
            name_en = name_obj.get('en', '') if isinstance(name_obj, dict) else str(name_obj)
            name_ne = name_obj.get('ne', '') if isinstance(name_obj, dict) else str(name_obj)

            role_obj = author.get('role', {})
            role_en = role_obj.get('en', '') if isinstance(role_obj, dict) else str(role_obj)
            role_ne = role_obj.get('ne', '') if isinstance(role_obj, dict) else str(role_obj)

            bio_obj = author.get('bio', {})
            bio_en = bio_obj.get('en', '') if isinstance(bio_obj, dict) else str(bio_obj)
            bio_ne = bio_obj.get('ne', '') if isinstance(bio_obj, dict) else str(bio_obj)

            obj, created = Author.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': name_en,
                    'name_en': name_en,
                    'name_ne': name_ne,
                    'role': role_en,
                    'role_en': role_en,
                    'role_ne': role_ne,
                    'bio': bio_en,
                    'bio_en': bio_en,
                    'bio_ne': bio_ne,
                    'avatar': author.get('avatar', ''),
                    'district': author.get('district', ''),
                }
            )
            author_map[author.get('id')] = obj
            author_map[slug] = obj

        self.stdout.write(f"  Seeded {Author.objects.count()} authors.")
        return author_map

    def seed_districts(self, districts_data):
        self.stdout.write("Seeding districts...")
        dist_map = {}
        for dist in districts_data:
            slug = dist.get('slug')
            name_obj = dist.get('name', {})
            name_en = name_obj.get('en', '') if isinstance(name_obj, dict) else str(name_obj)
            name_ne = name_obj.get('ne', '') if isinstance(name_obj, dict) else str(name_obj)

            history_obj = dist.get('history', {})
            history_en = history_obj.get('en', '') if isinstance(history_obj, dict) else str(history_obj or '')
            history_ne = history_obj.get('ne', '') if isinstance(history_obj, dict) else str(history_obj or '')

            district_obj, _ = District.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': name_en,
                    'name_en': name_en,
                    'name_ne': name_ne,
                    'history': history_en,
                    'history_en': history_en,
                    'history_ne': history_ne,
                    'accentColor': dist.get('accentColor', '#167A52'),
                    'heroImage': dist.get('heroImage', ''),
                    'latitude': dist.get('latitude'),
                    'longitude': dist.get('longitude'),
                    'meta_title': f"{name_en} - Sudurpashchim",
                    'meta_title_en': f"{name_en} - Sudurpashchim",
                    'meta_title_ne': f"{name_ne} - सुदूरपश्चिम",
                    'meta_description': history_en[:160] if history_en else name_en,
                    'meta_description_en': history_en[:160] if history_en else name_en,
                    'meta_description_ne': history_ne[:160] if history_ne else name_ne,
                }
            )
            dist_map[dist.get('id')] = district_obj
            dist_map[slug] = district_obj

            # DistrictTheme
            theme = dist.get('theme', {})
            if theme:
                DistrictTheme.objects.update_or_create(
                    district=district_obj,
                    defaults={
                        'primary': theme.get('primary', '#167A52'),
                        'dark': theme.get('dark', '#0E5139'),
                        'light': theme.get('light', '#E8F5E9'),
                        'border': theme.get('border', '#A5D6A7'),
                        'badgeBg': theme.get('badgeBg', '#E8F5E9'),
                        'badgeText': theme.get('badgeText', '#167A52'),
                        'gradient': theme.get('gradient', 'from-[#167A52] to-[#0E5139]'),
                    }
                )

            # DistrictStats
            stats = dist.get('stats', {})
            if stats:
                hq = stats.get('headquarters', {})
                hq_en = hq.get('en', '') if isinstance(hq, dict) else str(hq)
                hq_ne = hq.get('ne', '') if isinstance(hq, dict) else str(hq)

                mr = stats.get('majorRivers', {})
                mr_en = mr.get('en', '') if isinstance(mr, dict) else str(mr)
                mr_ne = mr.get('ne', '') if isinstance(mr, dict) else str(mr)

                palikas = stats.get('palikas', {})
                DistrictStats.objects.update_or_create(
                    district=district_obj,
                    defaults={
                        'area': stats.get('area', ''),
                        'population': stats.get('population', ''),
                        'headquarters': hq_en,
                        'headquarters_en': hq_en,
                        'headquarters_ne': hq_ne,
                        'elevation': stats.get('elevation', ''),
                        'palikas_total': palikas.get('total', 0),
                        'palikas_municipalities': palikas.get('municipalities', 0),
                        'palikas_rural': palikas.get('ruralMunicipalities', 0),
                        'majorRivers': mr_en,
                        'majorRivers_en': mr_en,
                        'majorRivers_ne': mr_ne,
                        'literacy': stats.get('literacy', ''),
                    }
                )

            # DistrictCulture
            culture = dist.get('culture', {})
            if culture:
                fd = culture.get('folkDance', {})
                fd_en = fd.get('en', '') if isinstance(fd, dict) else str(fd)
                fd_ne = fd.get('ne', '') if isinstance(fd, dict) else str(fd)

                fest = culture.get('festivals', {})
                fest_en = fest.get('en', '') if isinstance(fest, dict) else str(fest)
                fest_ne = fest.get('ne', '') if isinstance(fest, dict) else str(fest)

                cui = culture.get('cuisine', {})
                cui_en = cui.get('en', '') if isinstance(cui, dict) else str(cui)
                cui_ne = cui.get('ne', '') if isinstance(cui, dict) else str(cui)

                dia = culture.get('dialects', {})
                dia_en = dia.get('en', '') if isinstance(dia, dict) else str(dia)
                dia_ne = dia.get('ne', '') if isinstance(dia, dict) else str(dia)

                DistrictCulture.objects.update_or_create(
                    district=district_obj,
                    defaults={
                        'folkDance': fd_en,
                        'folkDance_en': fd_en,
                        'folkDance_ne': fd_ne,
                        'festivals': fest_en,
                        'festivals_en': fest_en,
                        'festivals_ne': fest_ne,
                        'cuisine': cui_en,
                        'cuisine_en': cui_en,
                        'cuisine_ne': cui_ne,
                        'dialects': dia_en,
                        'dialects_en': dia_en,
                        'dialects_ne': dia_ne,
                    }
                )

            # DistrictPlace
            places = dist.get('places', [])
            if places:
                DistrictPlace.objects.filter(district=district_obj).delete()
                for pl in places:
                    t_obj = pl.get('title', {})
                    t_en = t_obj.get('en', '') if isinstance(t_obj, dict) else str(t_obj)
                    t_ne = t_obj.get('ne', '') if isinstance(t_obj, dict) else str(t_obj)

                    d_obj = pl.get('description', {})
                    d_en = d_obj.get('en', '') if isinstance(d_obj, dict) else str(d_obj)
                    d_ne = d_obj.get('ne', '') if isinstance(d_obj, dict) else str(d_obj)

                    DistrictPlace.objects.create(
                        district=district_obj,
                        title=t_en,
                        title_en=t_en,
                        title_ne=t_ne,
                        description=d_en,
                        description_en=d_en,
                        description_ne=d_ne,
                        category=pl.get('category', 'nature'),
                        image=pl.get('image', ''),
                        highlight=pl.get('highlight', ''),
                    )

        self.stdout.write(f"  Seeded {District.objects.count()} districts with full themes/stats/places.")
        return dist_map

    def seed_articles(self, articles_data, cat_map, author_map, dist_map):
        self.stdout.write("Seeding articles...")
        art_map = {}
        for art in articles_data:
            raw_slug = art.get('slug')
            slug_val = (raw_slug.get('en') or raw_slug.get('ne')) if isinstance(raw_slug, dict) else raw_slug
            title_obj = art.get('title', {})
            title_en = title_obj.get('en', '') if isinstance(title_obj, dict) else str(title_obj)
            title_ne = title_obj.get('ne', '') if isinstance(title_obj, dict) else str(title_obj)

            excerpt_obj = art.get('excerpt', {})
            excerpt_en = excerpt_obj.get('en', '') if isinstance(excerpt_obj, dict) else str(excerpt_obj)
            excerpt_ne = excerpt_obj.get('ne', '') if isinstance(excerpt_obj, dict) else str(excerpt_obj)

            content_obj = art.get('content', {})
            content_en = content_obj.get('en', '') if isinstance(content_obj, dict) else str(content_obj)
            content_ne = content_obj.get('ne', '') if isinstance(content_obj, dict) else str(content_obj)

            cat_ref = art.get('category')
            cat_key = (cat_ref.get('slug') or cat_ref.get('id')) if isinstance(cat_ref, dict) else cat_ref
            category_instance = cat_map.get(cat_key) or Category.objects.filter(slug=cat_key).first()
            if not category_instance:
                category_instance = Category.objects.first()

            author_ref = art.get('author')
            author_key = (author_ref.get('slug') or author_ref.get('id')) if isinstance(author_ref, dict) else author_ref
            author_instance = author_map.get(author_key) or Author.objects.filter(slug=author_key).first()
            if not author_instance:
                author_instance = Author.objects.first()

            dist_ref = art.get('district')
            dist_key = (dist_ref.get('slug') or dist_ref.get('id')) if isinstance(dist_ref, dict) else dist_ref
            district_instance = dist_map.get(dist_key) if dist_key else None

            published_at_str = art.get('publishedAt')
            try:
                published_at = datetime.fromisoformat(published_at_str.replace('Z', '+00:00')) if published_at_str else timezone.now()
            except Exception:
                published_at = timezone.now()

            caption_obj = art.get('imageCaption', '')
            caption_en = caption_obj.get('en', '') if isinstance(caption_obj, dict) else str(caption_obj or '')
            caption_ne = caption_obj.get('ne', '') if isinstance(caption_obj, dict) else str(caption_obj or '')

            article_obj, _ = Article.objects.update_or_create(
                slug=slug_val,
                defaults={
                    'title': title_en,
                    'title_en': title_en,
                    'title_ne': title_ne,
                    'excerpt': excerpt_en,
                    'excerpt_en': excerpt_en,
                    'excerpt_ne': excerpt_ne,
                    'content': content_en,
                    'content_en': content_en,
                    'content_ne': content_ne,
                    'featuredImage': art.get('featuredImage', ''),
                    'imageCaption': caption_en,
                    'imageCaption_en': caption_en,
                    'imageCaption_ne': caption_ne,
                    'meta_title': title_en,
                    'meta_title_en': title_en,
                    'meta_title_ne': title_ne,
                    'meta_description': excerpt_en[:160],
                    'meta_description_en': excerpt_en[:160],
                    'meta_description_ne': excerpt_ne[:160],
                    'category': category_instance,
                    'author': author_instance,
                    'district': district_instance,
                    'status': 'published',
                    'publishedAt': published_at,
                    'featured': art.get('featured', False),
                    'breaking': art.get('breaking', False),
                    'popular': art.get('popular', False),
                    'readTime': art.get('readTime', 5),
                    'views': art.get('views', 0),
                    'likes': art.get('likes', 0),
                }
            )

            # Tags
            Tag.objects.filter(article=article_obj).delete()
            for t in art.get('tags', []):
                t_name = t.get('name', {}).get('en', '') if isinstance(t, dict) else str(t)
                if t_name and t_name.strip():
                    Tag.objects.create(article=article_obj, name=t_name.strip())

            art_map[art.get('id')] = article_obj
            art_map[slug_val] = article_obj
            if isinstance(raw_slug, dict):
                if raw_slug.get('en'):
                    art_map[raw_slug.get('en')] = article_obj
                if raw_slug.get('ne'):
                    art_map[raw_slug.get('ne')] = article_obj

        self.stdout.write(f"  Seeded {Article.objects.count()} articles.")
        return art_map

    def seed_comments(self, comments_dict, art_map):
        self.stdout.write("Seeding comments...")
        count = 0
        for art_key, comments_list in comments_dict.items():
            article = art_map.get(art_key)
            if not article:
                continue
            for comm in comments_list:
                created_str = comm.get('createdAt')
                try:
                    c_date = datetime.fromisoformat(created_str.replace('Z', '+00:00')) if created_str else timezone.now()
                except Exception:
                    c_date = timezone.now()

                ArticleComment.objects.update_or_create(
                    article=article,
                    authorName=comm.get('authorName', 'Anonymous'),
                    content=comm.get('content', ''),
                    defaults={
                        'authorLocation': comm.get('authorLocation', ''),
                        'createdAt': c_date,
                        'likes': comm.get('likes', 0),
                    }
                )
                count += 1
        self.stdout.write(f"  Seeded {count} article comments.")

    def seed_hotels(self, dist_map, cat_map):
        self.stdout.write("Seeding hotels, rooms, and amenities...")
        stay_cat = cat_map.get('stay') or Category.objects.filter(slug='stay').first()

        # Amenities
        amenities_data = [
            ("Free WiFi", "निःशुल्क वाइफाइ", "Wifi"),
            ("Swimming Pool", "पौडी पोखरी", "Waves"),
            ("Restaurant & Bar", "रेस्टुरेन्ट तथा बार", "Utensils"),
            ("Free Parking", "निःशुल्क पार्किङ", "Car"),
            ("Air Conditioning", "वातानुकूलित (AC)", "Wind"),
            ("Spa & Wellness", "स्पा तथा वेलनेस", "Sparkles"),
            ("Conference Hall", "सभा हल", "Users"),
            ("24/7 Room Service", "२४ घण्टा रुम सर्भिस", "Clock"),
            ("Garden & Lawn", "बगैँचा तथा खुला चउर", "Trees"),
            ("Airport Shuttle", "विमानस्थल शटल सेवा", "Bus"),
        ]
        amenity_objs = []
        for en, ne, icon in amenities_data:
            am, _ = Amenity.objects.update_or_create(
                name_en=en,
                defaults={'name': en, 'name_ne': ne, 'icon': icon}
            )
            amenity_objs.append(am)

        kailali = dist_map.get('kailali') or District.objects.filter(slug='kailali').first()
        kanchanpur = dist_map.get('kanchanpur') or District.objects.filter(slug='kanchanpur').first()
        doti = dist_map.get('doti') or District.objects.filter(slug='doti').first()
        bajhang = dist_map.get('bajhang') or District.objects.filter(slug='bajhang').first()

        hotels_data = [
            {
                "slug": "hotel-rubus",
                "district": kailali,
                "name_en": "Hotel Rubus",
                "name_ne": "होटल रुबस",
                "hotel_type_en": "Luxury Boutique Hotel",
                "hotel_type_ne": "विलासी बुटिक होटल",
                "address_en": "Main Road, Dhangadhi, Kailali",
                "address_ne": "मुख्य सडक, धनगढी, कैलाली",
                "municipality_en": "Dhangadhi Sub-Metropolitan City",
                "municipality_ne": "धनगढी उपमहानगरपालिका",
                "latitude": "28.6942",
                "longitude": "80.5936",
                "rating": 4.8,
                "reviews_count": 142,
                "hero_image": "/images/districts/kailali.jpg",
                "short_description_en": "Premium comfort and world-class hospitality in the heart of Dhangadhi.",
                "short_description_ne": "धनगढीको मुटुमा अवस्थित प्रिमियम सुविधा र विश्वस्तरीय आतिथ्यता।",
                "about_en": "Hotel Rubus is the leading luxury accommodation in Sudurpaschim, providing unmatched hospitality, fine dining, and modern corporate conference facilities for discerning business and leisure travelers.",
                "about_ne": "होटल रुबस सुदूरपश्चिमको एक अग्रणी विलासी होटल हो, जसले विशिष्ट व्यावसायिक र पर्यटकीय पाहुनाहरूलाई अतुलनीय आतिथ्यता, स्वादिष्ट परिकार र आधुनिक सम्मेलन कक्षहरू उपलब्ध गराउँछ।",
                "story_en": "Established with a grand vision to elevate hospitality standards in Far-Western Nepal, Hotel Rubus blends indigenous Tharu architectural nuances with cutting-edge modern comfort.",
                "story_ne": "सुदूरपश्चिम नेपालमा आतिथ्यताको स्तर उकास्ने लक्ष्यका साथ स्थापना भएको होटल रुबसले मौलिक थारू वास्तुकला र आधुनिक सुखसुविधाको उत्कृष्ट संयोजन प्रस्तुत गर्दछ।",
                "quote_text_en": "Hospitality is not just a profession, it is our deep-rooted cultural heritage.",
                "quote_text_ne": "आतिथ्यता केवल व्यवसाय होइन, यो हाम्रो गहिरो सांस्कृतिक संस्कार हो।",
                "quote_author": "Managing Director",
                "phone1": "+977-91-523456",
                "phone2": "+977-9858420111",
                "email": "info@hotelrubus.com",
                "website": "https://hotelrubus.com",
                "facebook_url": "https://facebook.com/hotelrubus",
                "highlights": [
                    {"en": "Rooftop Restaurant with Sunset View", "ne": "सूर्यास्तको दृश्य देखिने रुफटप रेस्टुरेन्ट"},
                    {"en": "Grand Banquet Hall for 500+ Guests", "ne": "५००+ पाहुना क्षमताको भव्य बैंक्वेट हल"},
                    {"en": "Organic Farm-to-Table Cuisine", "ne": "अर्गानिक कृषि उत्पादनबाट तयार परिकार"},
                    {"en": "Complimentary High-Speed WiFi", "ne": "निःशुल्क उच्च गतिको इन्टरनेट"}
                ],
                "reach_bus_en": "5 minutes from Dhangadhi Central Bus Terminal",
                "reach_bus_ne": "धनगढी मुख्य बस टर्मिनलबाट ५ मिनेट",
                "reach_airport_en": "15 minutes from Dhangadhi Airport (7 km)",
                "reach_airport_ne": "धनगढी विमानस्थलबाट १५ मिनेट (७ किमी)",
                "reach_highway_en": "Connected directly to East-West Highway Link",
                "reach_highway_ne": "पूर्व-पश्चिम राजमार्ग जोड्ने सडकसँग सिधा सम्पर्क",
                "rooms": [
                    {"name_en": "Deluxe King Room", "name_ne": "डिलक्स किङ रुम", "guests": 2, "bed_en": "1 King Bed", "bed_ne": "१ किङ बेड", "price": "Rs. 6,500"},
                    {"name_en": "Executive Suite", "name_ne": "एक्जिक्युटिभ सुइट", "guests": 3, "bed_en": "1 King + Sofa Bed", "bed_ne": "१ किङ + सोफा बेड", "price": "Rs. 10,500"},
                    {"name_en": "Family Twin Room", "name_ne": "पारिवारिक ट्विन रुम", "guests": 4, "bed_en": "2 Queen Beds", "bed_ne": "२ क्विन बेड", "price": "Rs. 8,000"},
                ],
                "nearby": [
                    {"name_en": "Jokhar Lake", "name_ne": "जोखर ताल", "dist_en": "2.5 km", "dist_ne": "२.५ किमी"},
                    {"name_en": "Mohana River Bird Sanctuary", "name_ne": "मोहाना नदी चरा अभयारण्य", "dist_en": "4.0 km", "dist_ne": "४.० किमी"},
                    {"name_en": "Ghodaghodi Ramsar Lake", "name_ne": "घोडाघोडी रामसार ताल", "dist_en": "48 km", "dist_ne": "४८ किमी"},
                ]
            },
            {
                "slug": "shuklaphanta-jungle-cottage",
                "district": kanchanpur,
                "name_en": "Shuklaphanta Jungle Cottage",
                "name_ne": "शुक्लाफाँटा जङ्गल कटेज",
                "hotel_type_en": "Eco Wildlife Resort",
                "hotel_type_ne": "इको वाइल्डलाइफ रिसोर्ट",
                "address_en": "Majhgaun, Bhimdatta, Kanchanpur",
                "address_ne": "माझगाउँ, भीमदत्त, कञ्चनपुर",
                "municipality_en": "Bhimdatta Municipality",
                "municipality_ne": "भीमदत्त नगरपालिका",
                "latitude": "28.8540",
                "longitude": "80.1802",
                "rating": 4.7,
                "reviews_count": 98,
                "hero_image": "/images/places/dodhara_chandani.jpg",
                "short_description_en": "Peaceful jungle lodge bordering the grasslands of Shuklaphanta National Park.",
                "short_description_ne": "शुक्लाफाँटा राष्ट्रिय निकुञ्जको घाँसे मैदान नजिकै शान्त जङ्गल लज।",
                "about_en": "Nestled near the entrance of Shuklaphanta National Park, our cottage provides tranquil eco-friendly chalets, guided wildlife safaris, and authentic Tharu cultural evenings.",
                "about_ne": "शुक्लाफाँटा राष्ट्रिय निकुञ्जको प्रवेशद्वार नजिकै अवस्थित यस कटेजले शान्त वातावरण, वन्यजन्तु सफारी र मौलिक थारू सांस्कृतिक कार्यक्रम प्रस्तुत गर्दछ।",
                "story_en": "Constructed with sustainable bamboo and indigenous red brick, the lodge supports wildlife conservation and local community development.",
                "story_ne": "स्थानीय बाँस र परम्परागत इँटाबाट निर्मित यो कटेजले वन्यजन्तु संरक्षण र स्थानीय समुदायको आयआर्जनमा टेवा पुर्‍याउँदै आएको छ।",
                "quote_text_en": "Listen to the wilderness, protect the flora and fauna.",
                "quote_text_ne": "प्रकृतिको आवाज सुनौं, वन र वन्यजन्तुको संरक्षण गरौं।",
                "quote_author": "Resort Naturalist",
                "phone1": "+977-99-521122",
                "email": "safari@shuklaphantacottage.com",
                "highlights": [
                    {"en": "Jeep Safari & Walking Safari in Shuklaphanta", "ne": "शुक्लाफाँटामा जिप तथा पैदल जङ्गल सफारी"},
                    {"en": "Traditional Tharu Cultural Dance Shows", "ne": "परम्परागत थारू सांस्कृतिक नाच प्रदर्शन"},
                    {"en": "Birdwatching Tours with Certified Naturalists", "ne": "प्रमाणित गाइडहरूसँग चरा अवलोकन भ्रमण"}
                ],
                "reach_bus_en": "10 minutes from Mahendranagar Bus Park",
                "reach_bus_ne": "महेन्द्रनगर बसपार्कबाट १० मिनेट",
                "reach_airport_en": "45 minutes from Dhangadhi Airport",
                "reach_airport_ne": "धनगढी विमानस्थलबाट ४५ मिनेट",
                "reach_highway_en": "5 km south of East-West Highway",
                "reach_highway_ne": "पूर्व-पश्चिम राजमार्गबाट ५ किमी दक्षिण",
                "rooms": [
                    {"name_en": "Eco Safari Cottage", "name_ne": "इको सफारी कटेज", "guests": 2, "bed_en": "1 Double Bed", "bed_ne": "१ डबल बेड", "price": "Rs. 5,000"},
                    {"name_en": "Jungle View Chalet", "name_ne": "जङ्गल भ्यु स्यालेट", "guests": 3, "bed_en": "1 King Bed", "bed_ne": "१ किङ बेड", "price": "Rs. 7,500"},
                ],
                "nearby": [
                    {"name_en": "Shuklaphanta National Park Gate", "name_ne": "शुक्लाफाँटा निकुञ्ज गेट", "dist_en": "1.0 km", "dist_ne": "१.० किमी"},
                    {"name_en": "Dodhara Chandani Suspension Bridge", "name_ne": "दोधारा चाँदनी झोलुङ्गे पुल", "dist_en": "18 km", "dist_ne": "१८ किमी"},
                ]
            },
            {
                "slug": "khaptad-eco-heritage-lodge",
                "district": doti,
                "name_en": "Khaptad Eco Heritage Lodge",
                "name_ne": "खप्तड इको हेरिटेज लज",
                "hotel_type_en": "Eco Lodge & Homestay",
                "hotel_type_ne": "इको लज तथा होमस्टे",
                "address_en": "Silgadhi, Doti",
                "address_ne": "सिलगढी, डोटी",
                "municipality_en": "Dipayal Silgadhi Municipality",
                "municipality_ne": "दिपायल सिलगढी नगरपालिका",
                "latitude": "29.2965",
                "longitude": "80.9856",
                "rating": 4.6,
                "reviews_count": 64,
                "hero_image": "/images/places/khaptad_national_park.jpg",
                "short_description_en": "Historic heritage retreat welcoming trekkers and spiritual travelers to Khaptad.",
                "short_description_ne": "खप्तड पदयात्री तथा आध्यात्मिक पर्यटकहरूका लागि ऐतिहासिक लज।",
                "about_en": "Located at the gateway to the sacred Khaptad plateau, offering cozy traditional hospitality, local Dotyali delicacies, and guided trail assistance.",
                "about_ne": "पवित्र खप्तड पाटनको प्रवेशद्वारमा अवस्थित, मौलिक डोटेली परिकार र न्यानो आतिथ्यता प्रदान गर्ने होमस्टे लज।",
                "story_en": "Preserving the architectural traditions of historic Silgadhi town with modern bedding and warm hospitality.",
                "story_ne": "ऐतिहासिक सिलगढी बजारको परम्परागत वास्तुकला जोगाउँदै पदयात्रीहरूलाई आधुनिक सुविधा प्रदान गरिँदै आएको छ।",
                "quote_text_en": "The tranquility of Khaptad begins right at your doorstep.",
                "quote_text_ne": "खप्तडको शान्ति र आनन्द तपाईंको ढोकाबाटै सुरु हुन्छ।",
                "quote_author": "Lodge Host",
                "phone1": "+977-94-420234",
                "email": "stay@khaptadheritagelodge.com",
                "highlights": [
                    {"en": "Trekking Gear Rental & Route Guides", "ne": "पदयात्रा सामग्री भाडा तथा गाइड सुविधा"},
                    {"en": "Authentic Dotyali Organic Meals", "ne": "मौलिक डोटेली अर्गानिक खानपान"},
                    {"en": "Panoramic Himalayan Views", "ne": "मनोरम हिमाली दृश्यावलोकन"}
                ],
                "reach_bus_en": "Located in Silgadhi Bazaar, walking distance from bus station",
                "reach_bus_ne": "सिलगढी बजारमै अवस्थित, बस स्टेसनबाट हिँड्ने दूरीमा",
                "reach_airport_en": "20 minutes from Dipayal Airport",
                "reach_airport_ne": "दिपायल विमानस्थलबाट २० मिनेट",
                "reach_highway_en": "Directly accessible via KI Singh Highway",
                "reach_highway_ne": "केआई सिंह राजमार्गबाट सिधा पहुँच",
                "rooms": [
                    {"name_en": "Standard Mountain Room", "name_ne": "स्ट्यान्डर्ड माउन्टेन रुम", "guests": 2, "bed_en": "2 Single Beds", "bed_ne": "२ सिंगल बेड", "price": "Rs. 2,800"},
                    {"name_en": "Deluxe Family Room", "name_ne": "डिलक्स पारिवारिक रुम", "guests": 4, "bed_en": "2 Double Beds", "bed_ne": "२ डबल बेड", "price": "Rs. 4,500"},
                ],
                "nearby": [
                    {"name_en": "Shaileshwori Temple", "name_ne": "शैलेश्वरी मन्दिर", "dist_en": "1.2 km", "dist_ne": "१.२ किमी"},
                    {"name_en": "Khaptad National Park Entrance (Jhigrana)", "name_ne": "खप्तड निकुञ्ज प्रवेशद्वार (झिग्राना)", "dist_en": "15 km", "dist_ne": "१५ किमी"},
                ]
            },
            {
                "slug": "saipal-himalayan-resort",
                "district": bajhang,
                "name_en": "Saipal Himalayan Resort",
                "name_ne": "सैपाल हिमालयन रिसोर्ट",
                "hotel_type_en": "Mountain Resort & Trekking Base",
                "hotel_type_ne": "हिमाली रिसोर्ट तथा पदयात्रा बेस",
                "address_en": "Chainpur, Bajhang",
                "address_ne": "चैनपुर, बझाङ",
                "municipality_en": "Jayaprithvi Municipality",
                "municipality_ne": "जयपृथ्वी नगरपालिका",
                "latitude": "29.5600",
                "longitude": "81.2000",
                "rating": 4.9,
                "reviews_count": 52,
                "hero_image": "/images/places/surma_sarovar.jpg",
                "short_description_en": "Magnificent views of Mount Saipal with warm mountain hospitality.",
                "short_description_ne": "सैपाल हिमालको उत्कृष्ट दृश्यसहित न्यानो हिमाली आतिथ्यता।",
                "about_en": "Surrounded by rivers and snow-capped peaks, Saipal Himalayan Resort offers travelers a comfortable haven in the serene heights of Bajhang.",
                "about_ne": "हिमनदी र हिउँले ढाकिएका शिखरहरूले घेरिएको यो रिसोर्टले बझाङको शान्त वातावरणमा आरामदायी बसाइको ग्यारेन्टी गर्दछ।",
                "story_en": "Named after the iconic Mount Saipal (7,031m), celebrated for serving organic Himalayan trout, wild honey, and local grains.",
                "story_ne": "भव्य सैपाल हिमाल (७,०३१ मि.) को नामबाट स्थापित, स्थानीय असला माछा र हिमाली परिकारका लागि प्रसिद्ध।",
                "quote_text_en": "Discover the untouched beauty of Far-Western Himalayas.",
                "quote_text_ne": "सुदूरपश्चिमका अछुतो र मनमोहक हिमालहरूको सौन्दर्य महसुस गर्नुहोस्।",
                "quote_author": "Resort Founder",
                "phone1": "+977-92-421111",
                "email": "booking@saipalresort.com",
                "highlights": [
                    {"en": "Uninterrupted Vista of Mount Saipal", "ne": "सैपाल हिमालको निर्बाध दृश्यावलोकन"},
                    {"en": "Fresh Himalayan River Trout Dining", "ne": "ताजा हिमाली असला माछाको परिकार"},
                    {"en": "High-Altitude Trekking Logistics & Porter Services", "ne": "उच्च हिमाली पदयात्रा व्यवस्थापन तथा भरिया सेवा"}
                ],
                "reach_bus_en": "Central Chainpur Bazaar, near Seti river bridge",
                "reach_bus_ne": "चैनपुर बजार, सेती नदी पुल नजिकै",
                "reach_airport_en": "10 minutes from Bajhang Airport (Chainpur)",
                "reach_airport_ne": "बझाङ विमानस्थल (चैनपुर) बाट १० मिनेट",
                "reach_highway_en": "End of Jaya Prithvi Highway",
                "reach_highway_ne": "जयपृथ्वी राजमार्गको अन्तिम विन्दु",
                "rooms": [
                    {"name_en": "Himalayan View Room", "name_ne": "हिमालयन भ्यु रुम", "guests": 2, "bed_en": "1 King Bed", "bed_ne": "१ किङ बेड", "price": "Rs. 4,000"},
                    {"name_en": "Trekker Suite", "name_ne": "ट्रेकर सुइट", "guests": 3, "bed_en": "3 Single Beds", "bed_ne": "३ सिंगल बेड", "price": "Rs. 5,500"},
                ],
                "nearby": [
                    {"name_en": "Surma Sarovar Lake Trailhead", "name_ne": "सुर्मा सरोवर पदमार्ग", "dist_en": "25 km", "dist_ne": "२५ किमी"},
                    {"name_en": "Seti River Walk", "name_ne": "सेती नदी किनार", "dist_en": "0.5 km", "dist_ne": "०.५ किमी"},
                ]
            }
        ]

        for h_data in hotels_data:
            dist = h_data.get('district')
            hotel_obj, _ = Hotel.objects.update_or_create(
                slug=h_data['slug'],
                defaults={
                    'category': stay_cat,
                    'district': dist,
                    'name': h_data['name_en'],
                    'name_en': h_data['name_en'],
                    'name_ne': h_data['name_ne'],
                    'hotel_type': h_data['hotel_type_en'],
                    'hotel_type_en': h_data['hotel_type_en'],
                    'hotel_type_ne': h_data['hotel_type_ne'],
                    'address': h_data['address_en'],
                    'address_en': h_data['address_en'],
                    'address_ne': h_data['address_ne'],
                    'municipality': h_data['municipality_en'],
                    'municipality_en': h_data['municipality_en'],
                    'municipality_ne': h_data['municipality_ne'],
                    'latitude': h_data['latitude'],
                    'longitude': h_data['longitude'],
                    'rating': h_data['rating'],
                    'reviews_count': h_data['reviews_count'],
                    'hero_image': h_data['hero_image'],
                    'short_description': h_data['short_description_en'],
                    'short_description_en': h_data['short_description_en'],
                    'short_description_ne': h_data['short_description_ne'],
                    'about': h_data['about_en'],
                    'about_en': h_data['about_en'],
                    'about_ne': h_data['about_ne'],
                    'story': h_data['story_en'],
                    'story_en': h_data['story_en'],
                    'story_ne': h_data['story_ne'],
                    'quote_text': h_data['quote_text_en'],
                    'quote_text_en': h_data['quote_text_en'],
                    'quote_text_ne': h_data['quote_text_ne'],
                    'quote_author': h_data['quote_author'],
                    'phone1': h_data['phone1'],
                    'phone2': h_data.get('phone2', ''),
                    'email': h_data.get('email', ''),
                    'website': h_data.get('website', ''),
                    'facebook_url': h_data.get('facebook_url', ''),
                    'highlights': h_data['highlights'],
                    'reach_bus': h_data['reach_bus_en'],
                    'reach_bus_en': h_data['reach_bus_en'],
                    'reach_bus_ne': h_data['reach_bus_ne'],
                    'reach_airport': h_data['reach_airport_en'],
                    'reach_airport_en': h_data['reach_airport_en'],
                    'reach_airport_ne': h_data['reach_airport_ne'],
                    'reach_highway': h_data['reach_highway_en'],
                    'reach_highway_en': h_data['reach_highway_en'],
                    'reach_highway_ne': h_data['reach_highway_ne'],
                }
            )
            hotel_obj.amenities.set(amenity_objs)

            # Rooms
            HotelRoom.objects.filter(hotel=hotel_obj).delete()
            for r in h_data.get('rooms', []):
                price_str = ''.join(c for c in str(r.get('price', '')) if c.isdigit() or c == '.')
                price_num = float(price_str) if price_str else None
                HotelRoom.objects.create(
                    hotel=hotel_obj,
                    name=r['name_en'],
                    name_en=r['name_en'],
                    name_ne=r['name_ne'],
                    guests=r['guests'],
                    bed_type=r['bed_en'],
                    bed_type_en=r['bed_en'],
                    bed_type_ne=r['bed_ne'],
                    price=price_num,
                    image=h_data['hero_image'],
                )

            # Nearby places
            HotelNearbyPlace.objects.filter(hotel=hotel_obj).delete()
            for n in h_data.get('nearby', []):
                HotelNearbyPlace.objects.create(
                    hotel=hotel_obj,
                    name=n['name_en'],
                    name_en=n['name_en'],
                    name_ne=n['name_ne'],
                    distance=n['dist_en'],
                    distance_en=n['dist_en'],
                    distance_ne=n['dist_ne'],
                )

            # Gallery
            HotelGallery.objects.filter(hotel=hotel_obj).delete()
            HotelGallery.objects.create(
                hotel=hotel_obj,
                image=h_data['hero_image'],
                caption_en=f"{h_data['name_en']} Exterior View",
                caption_ne=f"{h_data['name_ne']} बाह्य दृश्य",
            )

        self.stdout.write(f"  Seeded {Hotel.objects.count()} hotels with rooms, amenities, and nearby places.")

    def seed_popup_ads(self):
        self.stdout.write("Seeding popup roadblock ads...")
        ad, created = PopupAd.objects.update_or_create(
            title_en="Fly with Yeti Airlines to Dhangadhi",
            defaults={
                'title': "Fly with Yeti Airlines to Dhangadhi",
                'title_ne': "यती एयरलाइन्सबाट धनगढीको उडान",
                'image_url': "/images/ads/roadblock_yeti_ad.jpg",
                'target_url': "https://www.yetiairlines.com",
                'advertiser': "Yeti Airlines",
                'duration_seconds': 6,
                'is_active': True,
            }
        )
        self.stdout.write(f"  {'Created' if created else 'Updated'} active PopupAd: {ad}")
