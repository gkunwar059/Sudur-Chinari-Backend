from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from api.models import (
    Amenity,
    Article,
    ArticleComment,
    Author,
    BreakingNews,
    Category,
    District,
    DistrictCulture,
    DistrictPlace,
    DistrictSliderImage,
    DistrictStats,
    DistrictTheme,
    HomePagePlacement,
    Hotel,
    HotelGallery,
    HotelNearbyPlace,
    HotelRoom,
    Partner,
    PhotoStory,
    PopupAd,
    Tag,
    UserProfile,
    VideoItem,
)

User = get_user_model()
MIN_ROWS = 50


class Command(BaseCommand):
    help = f"Ensure every project table contains at least {MIN_ROWS} rows."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(f"Ensuring at least {MIN_ROWS} rows per table...")
        self.ensure_user_profiles()
        self.ensure_districts()
        self.ensure_district_details()
        self.ensure_district_slider_images()
        self.ensure_district_places()
        self.ensure_partners()
        self.ensure_categories()
        self.ensure_authors()
        self.ensure_articles()
        self.ensure_tags()
        self.ensure_comments()
        self.ensure_breaking_news()
        self.ensure_home_page_placements()
        self.ensure_amenities()
        self.ensure_hotels()
        self.ensure_hotel_rooms()
        self.ensure_hotel_galleries()
        self.ensure_hotel_nearby_places()
        self.ensure_videos()
        self.ensure_photo_stories()
        self.ensure_popup_ads()
        call_command("seed_images")
        self.print_summary()

    def report(self, label, model):
        count = model.objects.count()
        status = "OK" if count >= MIN_ROWS else "LOW"
        self.stdout.write(f"  {label}: {count} [{status}]")

    def ensure_user_profiles(self):
        index = 1
        for user in User.objects.filter(profile__isnull=True):
            UserProfile.objects.update_or_create(
                user=user, defaults={"phone": self.unique_phone(index)}
            )
            index += 1

        index = 1
        while UserProfile.objects.count() < MIN_ROWS:
            username = f"seeduser{index:02d}"
            user = User.objects.filter(username=username).first()
            if user is None:
                user = User.objects.create_user(
                    username=username,
                    email=f"{username}@example.com",
                    password="seedpass123",
                    first_name="Seed",
                    last_name=f"User {index}",
                )
            UserProfile.objects.get_or_create(
                user=user, defaults={"phone": self.unique_phone(index)}
            )
            index += 1

        self.report("user profiles", UserProfile)

    def unique_phone(self, start):
        number = start
        while UserProfile.objects.filter(phone=f"98{number:08d}").exists():
            number += 1
        return f"98{number:08d}"

    def ensure_districts(self):
        index = 1
        while District.objects.count() < MIN_ROWS:
            name_en = f"Demo District {index:02d}"
            name_ne = f"नमुना जिल्ला {index:02d}"
            District.objects.update_or_create(
                slug=f"demo-district-{index:02d}",
                defaults={
                    "name": name_en,
                    "name_en": name_en,
                    "name_ne": name_ne,
                    "description": f"Demo description for {name_en}.",
                    "description_en": f"Demo description for {name_en}.",
                    "description_ne": f"{name_ne} को लागि नमुना विवरण।",
                    "history": f"Demo history for {name_en}.",
                    "history_en": f"Demo history for {name_en}.",
                    "history_ne": f"{name_ne} को नमुना इतिहास।",
                    "meta_title": f"{name_en} - Sudurpashchim",
                    "meta_title_en": f"{name_en} - Sudurpashchim",
                    "meta_title_ne": f"{name_ne} - सुदूरपश्चिम",
                    "meta_description": f"Demo district profile for {name_en}.",
                    "meta_description_en": f"Demo district profile for {name_en}.",
                    "meta_description_ne": f"{name_ne} को नमुना प्रोफाइल।",
                    "accentColor": "#05965B",
                    "heroImage": "/images/districts/kailali.jpg",
                    "latitude": 28.5 + index / 100,
                    "longitude": 80.5 + index / 100,
                },
            )
            index += 1

        self.report("districts", District)

    def ensure_district_details(self):
        for district in District.objects.all():
            DistrictTheme.objects.get_or_create(
                district=district,
                defaults={
                    "primary": "#05965B",
                    "dark": "#046A42",
                    "light": "#E8F5E9",
                    "border": "#A5D6A7",
                    "badgeBg": "#E8F5E9",
                    "badgeText": "#05965B",
                    "gradient": "from-[#05965B] to-[#046A42]",
                },
            )
            DistrictStats.objects.get_or_create(
                district=district,
                defaults={
                    "area": "1,500 km²",
                    "population": "150,000",
                    "headquarters": "Demo Headquarters",
                    "headquarters_en": "Demo Headquarters",
                    "headquarters_ne": "नमुना सदरमुकाम",
                    "elevation": "1,200 m",
                    "palikas_total": 9,
                    "palikas_municipalities": 4,
                    "palikas_rural": 5,
                    "majorRivers": "Seti, Mahakali",
                    "majorRivers_en": "Seti, Mahakali",
                    "majorRivers_ne": "सेती, महाकाली",
                    "literacy": "78%",
                },
            )
            DistrictCulture.objects.get_or_create(
                district=district,
                defaults={
                    "folkDance": "Demo folk dance traditions.",
                    "folkDance_en": "Demo folk dance traditions.",
                    "folkDance_ne": "नमुना लोकनृत्य परम्परा।",
                    "festivals": "Demo festivals celebrated across the district.",
                    "festivals_en": "Demo festivals celebrated across the district.",
                    "festivals_ne": "जिल्लाभर मनाइने नमुना चाडपर्वहरू।",
                    "cuisine": "Demo local cuisine.",
                    "cuisine_en": "Demo local cuisine.",
                    "cuisine_ne": "नमुना स्थानीय परिकार।",
                    "dialects": "Demo local dialects.",
                    "dialects_en": "Demo local dialects.",
                    "dialects_ne": "नमुना स्थानीय बोली।",
                },
            )

        self.report("district themes", DistrictTheme)
        self.report("district stats", DistrictStats)
        self.report("district culture", DistrictCulture)

    def ensure_district_slider_images(self):
        districts = list(District.objects.all())
        index = 1
        while DistrictSliderImage.objects.count() < MIN_ROWS:
            district = districts[(index - 1) % len(districts)]
            DistrictSliderImage.objects.create(
                district=district,
                image=f"districts/slider/demo-{index:02d}.jpg",
                caption=f"Demo slider image {index:02d}",
                caption_en=f"Demo slider image {index:02d}",
                caption_ne=f"नमुना स्लाइडर तस्बिर {index:02d}",
                order=index,
            )
            index += 1

        self.report("district slider images", DistrictSliderImage)

    def ensure_district_places(self):
        districts = list(District.objects.all())
        categories = ["nature", "culture", "heritage", "adventure", "religious"]
        index = 1
        while DistrictPlace.objects.count() < MIN_ROWS:
            district = districts[(index - 1) % len(districts)]
            title_en = f"Demo Place {index:02d}"
            title_ne = f"नमुना स्थल {index:02d}"
            DistrictPlace.objects.create(
                district=district,
                title=title_en,
                title_en=title_en,
                title_ne=title_ne,
                description=f"A demo place to visit in {district.name_en or district.name}.",
                description_en=f"A demo place to visit in {district.name_en or district.name}.",
                description_ne=f"{district.name_ne or district.name} मा घुम्ने नमुना स्थल।",
                category=categories[(index - 1) % len(categories)],
                image="/images/places/dodhara_chandani.jpg",
                highlight="Demo highlight",
            )
            index += 1

        self.report("district places", DistrictPlace)

    def ensure_partners(self):
        districts = list(District.objects.all())
        index = 1
        while Partner.objects.count() < MIN_ROWS:
            name_en = f"Demo Partner {index:02d}"
            name_ne = f"नमुना साझेदार {index:02d}"
            role_en = "Community Partner"
            role_ne = "सामुदायिक साझेदार"
            Partner.objects.create(
                name=name_en,
                name_en=name_en,
                name_ne=name_ne,
                role=role_en,
                role_en=role_en,
                role_ne=role_ne,
                url=f"https://example.com/partners/{index:02d}",
                district=districts[(index - 1) % len(districts)] if districts else None,
            )
            index += 1

        self.report("partners", Partner)

    def ensure_categories(self):
        index = 1
        while Category.objects.count() < MIN_ROWS:
            name_en = f"Demo Category {index:02d}"
            name_ne = f"नमुना श्रेणी {index:02d}"
            Category.objects.update_or_create(
                slug=f"demo-category-{index:02d}",
                defaults={
                    "name": name_en,
                    "name_en": name_en,
                    "name_ne": name_ne,
                    "description": f"Demo category {index:02d}.",
                    "order": 900 + index,
                    "show_in_menu": False,
                    "layout_type": "default",
                    "icon": "•",
                },
            )
            index += 1

        self.report("categories", Category)

    def ensure_authors(self):
        index = 1
        while Author.objects.count() < MIN_ROWS:
            name_en = f"Demo Author {index:02d}"
            name_ne = f"नमुना लेखक {index:02d}"
            role_en = "Staff Reporter"
            role_ne = "कर्मचारी पत्रकार"
            Author.objects.update_or_create(
                slug=f"demo-author-{index:02d}",
                defaults={
                    "name": name_en,
                    "name_en": name_en,
                    "name_ne": name_ne,
                    "bio": f"Demo biography for {name_en}.",
                    "bio_en": f"Demo biography for {name_en}.",
                    "bio_ne": f"{name_ne} को नमुना परिचय।",
                    "role": role_en,
                    "role_en": role_en,
                    "role_ne": role_ne,
                    "district": "Demo District",
                },
            )
            index += 1

        self.report("authors", Author)

    def ensure_articles(self):
        category = (
            Category.objects.exclude(layout_type__in=["stay", "stayor_hotel"]).first()
            or Category.objects.create(
                slug="demo-news",
                name="Demo News",
                name_en="Demo News",
                name_ne="नमुना समाचार",
                layout_type="news",
            )
        )
        authors = list(Author.objects.all())
        districts = list(District.objects.all())
        index = 1
        while Article.objects.count() < MIN_ROWS:
            title_en = f"Demo Article {index:02d}"
            title_ne = f"नमुना समाचार {index:02d}"
            excerpt_en = f"A short demo excerpt for article {index:02d}."
            excerpt_ne = f"लेख {index:02d} को छोटो नमुना सारांश।"
            Article.objects.update_or_create(
                slug=f"demo-article-{index:02d}",
                defaults={
                    "title": title_en,
                    "title_en": title_en,
                    "title_ne": title_ne,
                    "excerpt": excerpt_en,
                    "excerpt_en": excerpt_en,
                    "excerpt_ne": excerpt_ne,
                    "content": f"<p>{excerpt_en}</p>",
                    "content_en": f"<p>{excerpt_en}</p>",
                    "content_ne": f"<p>{excerpt_ne}</p>",
                    "featuredImage": "/images/articles/demo.jpg",
                    "imageCaption": "Demo image",
                    "imageCaption_en": "Demo image",
                    "imageCaption_ne": "नमुना तस्बिर",
                    "meta_title": title_en,
                    "meta_title_en": title_en,
                    "meta_title_ne": title_ne,
                    "meta_description": excerpt_en,
                    "meta_description_en": excerpt_en,
                    "meta_description_ne": excerpt_ne,
                    "author": authors[(index - 1) % len(authors)],
                    "category": category,
                    "district": districts[(index - 1) % len(districts)] if districts else None,
                    "status": "published",
                    "publishedAt": timezone.now() - timedelta(hours=index),
                    "featured": index % 10 == 0,
                    "breaking": index % 25 == 0,
                    "popular": index % 5 == 0,
                    "readTime": 3 + index % 10,
                    "views": index * 37,
                    "likes": index * 3,
                },
            )
            index += 1

        self.report("articles", Article)

    def ensure_tags(self):
        articles = list(Article.objects.all())
        index = 1
        while Tag.objects.count() < MIN_ROWS:
            article = articles[(index - 1) % len(articles)]
            Tag.objects.create(article=article, name=f"Demo Tag {index:02d}")
            index += 1

        self.report("tags", Tag)

    def ensure_comments(self):
        articles = list(Article.objects.all())
        index = 1
        while ArticleComment.objects.count() < MIN_ROWS:
            article = articles[(index - 1) % len(articles)]
            ArticleComment.objects.create(
                article=article,
                authorName=f"Demo Reader {index:02d}",
                authorLocation="Dhangadhi",
                content=f"Demo comment number {index:02d}.",
                likes=index % 12,
            )
            index += 1

        self.report("comments", ArticleComment)

    def ensure_breaking_news(self):
        index = 1
        while BreakingNews.objects.count() < MIN_ROWS:
            text_en = f"Demo breaking news {index:02d}"
            BreakingNews.objects.create(
                text=text_en,
                text_en=text_en,
                text_ne=f"नमुना ताजा समाचार {index:02d}",
                href=f"https://example.com/breaking/{index:02d}",
            )
            index += 1

        self.report("breaking news", BreakingNews)

    def ensure_home_page_placements(self):
        articles = list(Article.objects.all())
        index = 1
        while HomePagePlacement.objects.count() < MIN_ROWS:
            placement, _ = HomePagePlacement.objects.get_or_create(
                section_name=f"Demo Section {index:02d}"
            )
            if articles:
                placement.articles.set(
                    [articles[(index - 1) % len(articles)], articles[index % len(articles)]]
                )
            index += 1

        self.report("homepage placements", HomePagePlacement)

    def ensure_amenities(self):
        icons = ["Wifi", "Coffee", "Car", "Waves", "Wind", "Clock", "Trees", "Bus", "Users", "Sparkles"]
        index = 1
        while Amenity.objects.count() < MIN_ROWS:
            name_en = f"Demo Amenity {index:02d}"
            Amenity.objects.update_or_create(
                name=name_en,
                defaults={
                    "name_en": name_en,
                    "name_ne": f"नमुना सुविधा {index:02d}",
                    "icon": icons[(index - 1) % len(icons)],
                },
            )
            index += 1

        self.report("amenities", Amenity)

    def ensure_hotels(self):
        stay_category = Category.objects.filter(slug="stay").first()
        if stay_category is None:
            stay_category = Category.objects.create(
                slug="stay",
                name="Hotels & Stay",
                name_en="Hotels & Stay",
                name_ne="होटल तथा बासस्थान",
                layout_type="stay",
                show_in_menu=True,
            )
        districts = list(District.objects.all())
        amenities = list(Amenity.objects.all())
        index = 1
        while Hotel.objects.count() < MIN_ROWS:
            name_en = f"Demo Hotel {index:02d}"
            name_ne = f"नमुना होटल {index:02d}"
            hotel_type_en = "Demo Hotel"
            hotel_type_ne = "नमुना होटल"
            address_en = f"Demo Road, Ward {index}, Nepal"
            address_ne = f"नमुना सडक, वडा {index}, नेपाल"
            municipality_en = "Demo Municipality"
            municipality_ne = "नमुना नगरपालिका"
            hotel, _ = Hotel.objects.update_or_create(
                slug=f"demo-hotel-{index:02d}",
                defaults={
                    "name": name_en,
                    "name_en": name_en,
                    "name_ne": name_ne,
                    "hotel_type": hotel_type_en,
                    "hotel_type_en": hotel_type_en,
                    "hotel_type_ne": hotel_type_ne,
                    "category": stay_category,
                    "district": districts[(index - 1) % len(districts)] if districts else None,
                    "address": address_en,
                    "address_en": address_en,
                    "address_ne": address_ne,
                    "municipality": municipality_en,
                    "municipality_en": municipality_en,
                    "municipality_ne": municipality_ne,
                    "latitude": f"28.{index:04d}",
                    "longitude": f"80.{index:04d}",
                    "rating": Decimal("4.5"),
                    "reviews_count": index * 7,
                    "hero_image": "/images/districts/kailali.jpg",
                    "short_description": f"Demo short description for {name_en}.",
                    "short_description_en": f"Demo short description for {name_en}.",
                    "short_description_ne": f"{name_ne} को छोटो नमुना विवरण।",
                    "about": f"Demo about text for {name_en}.",
                    "about_en": f"Demo about text for {name_en}.",
                    "about_ne": f"{name_ne} को नमुना विवरण।",
                    "story": f"Demo story for {name_en}.",
                    "story_en": f"Demo story for {name_en}.",
                    "story_ne": f"{name_ne} को नमुना कथा।",
                    "quote_text": "Demo quote.",
                    "quote_text_en": "Demo quote.",
                    "quote_text_ne": "नमुना उद्धरण।",
                    "quote_author": "Demo Manager",
                    "phone1": f"+977-98{index:08d}",
                    "email": f"demo{index:02d}@example.com",
                    "website": f"https://example.com/hotels/{index:02d}",
                    "highlights": ["Demo highlight one", "Demo highlight two"],
                    "reach_bus": "5 minutes from the bus park",
                    "reach_bus_en": "5 minutes from the bus park",
                    "reach_bus_ne": "बसपार्कबाट ५ मिनेट",
                    "reach_airport": "30 minutes from the airport",
                    "reach_airport_en": "30 minutes from the airport",
                    "reach_airport_ne": "विमानस्थलबाट ३० मिनेट",
                    "reach_highway": "Near the highway",
                    "reach_highway_en": "Near the highway",
                    "reach_highway_ne": "राजमार्ग नजिकै",
                },
            )
            if amenities:
                hotel.amenities.set(
                    [
                        amenities[(index - 1) % len(amenities)],
                        amenities[index % len(amenities)],
                    ]
                )
            index += 1

        self.report("hotels", Hotel)

    def ensure_hotel_rooms(self):
        hotels = list(Hotel.objects.all())
        index = 1
        while HotelRoom.objects.count() < MIN_ROWS:
            hotel = hotels[(index - 1) % len(hotels)]
            name_en = f"Demo Room {index:02d}"
            bed_en = "1 King Bed"
            HotelRoom.objects.create(
                hotel=hotel,
                name=name_en,
                name_en=name_en,
                name_ne=f"नमुना कोठा {index:02d}",
                guests=2 + index % 3,
                bed_type=bed_en,
                bed_type_en=bed_en,
                bed_type_ne="१ किङ बेड",
                image="/images/districts/kailali.jpg",
                price=Decimal("3500.00") + index * 100,
            )
            index += 1

        self.report("hotel rooms", HotelRoom)

    def ensure_hotel_galleries(self):
        hotels = list(Hotel.objects.all())
        index = 1
        while HotelGallery.objects.count() < MIN_ROWS:
            hotel = hotels[(index - 1) % len(hotels)]
            caption_en = f"Demo gallery image {index:02d}"
            HotelGallery.objects.create(
                hotel=hotel,
                image="/images/districts/kailali.jpg",
                caption=caption_en,
                caption_en=caption_en,
                caption_ne=f"नमुना ग्यालरी तस्बिर {index:02d}",
            )
            index += 1

        self.report("hotel galleries", HotelGallery)

    def ensure_hotel_nearby_places(self):
        hotels = list(Hotel.objects.all())
        index = 1
        while HotelNearbyPlace.objects.count() < MIN_ROWS:
            hotel = hotels[(index - 1) % len(hotels)]
            name_en = f"Demo Nearby Place {index:02d}"
            distance_en = f"{index % 20 + 1} km"
            HotelNearbyPlace.objects.create(
                hotel=hotel,
                name=name_en,
                name_en=name_en,
                name_ne=f"नमुना नजिकको स्थल {index:02d}",
                distance=distance_en,
                distance_en=distance_en,
                distance_ne=f"{index % 20 + 1} किमी",
            )
            index += 1

        self.report("hotel nearby places", HotelNearbyPlace)

    def ensure_videos(self):
        districts = list(District.objects.all())
        index = 1
        while VideoItem.objects.count() < MIN_ROWS:
            title_en = f"Demo Video {index:02d}"
            VideoItem.objects.create(
                title=title_en,
                title_en=title_en,
                title_ne=f"नमुना भिडियो {index:02d}",
                thumbnail=f"https://example.com/videos/{index:02d}.jpg",
                duration=f"0{index % 9 + 1}:{index * 7 % 60:02d}",
                views=index * 123,
                publishedAt=timezone.now() - timedelta(days=index),
                district=districts[(index - 1) % len(districts)] if districts else None,
                isShort=index % 4 == 0,
            )
            index += 1

        self.report("videos", VideoItem)

    def ensure_photo_stories(self):
        districts = list(District.objects.all())
        index = 1
        while PhotoStory.objects.count() < MIN_ROWS:
            title_en = f"Demo Photo Story {index:02d}"
            PhotoStory.objects.create(
                title=title_en,
                title_en=title_en,
                title_ne=f"नमुना फोटो कथा {index:02d}",
                description=f"Demo photo story description {index:02d}.",
                description_en=f"Demo photo story description {index:02d}.",
                description_ne=f"नमुना फोटो कथा विवरण {index:02d}।",
                coverImage=f"https://example.com/photos/{index:02d}.jpg",
                imageCount=5 + index % 15,
                photographer=f"Demo Photographer {index:02d}",
                publishedAt=timezone.now() - timedelta(days=index),
                district=districts[(index - 1) % len(districts)] if districts else None,
            )
            index += 1

        self.report("photo stories", PhotoStory)

    def ensure_popup_ads(self):
        index = 1
        while PopupAd.objects.count() < MIN_ROWS:
            title_en = f"Demo Popup Ad {index:02d}"
            PopupAd.objects.create(
                title=title_en,
                title_en=title_en,
                title_ne=f"नमुना विज्ञापन {index:02d}",
                image_url=f"https://example.com/ads/{index:02d}.jpg",
                target_url=f"https://example.com/ads/{index:02d}/target",
                advertiser=f"Demo Advertiser {index:02d}",
                duration_seconds=5 + index % 10,
                is_active=index % 5 != 0,
            )
            index += 1

        self.report("popup ads", PopupAd)

    def print_summary(self):
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Minimum row count check ({MIN_ROWS}):"))
        models = [
            ("UserProfile", UserProfile),
            ("District", District),
            ("DistrictSliderImage", DistrictSliderImage),
            ("DistrictTheme", DistrictTheme),
            ("DistrictStats", DistrictStats),
            ("DistrictCulture", DistrictCulture),
            ("DistrictPlace", DistrictPlace),
            ("Partner", Partner),
            ("Category", Category),
            ("Author", Author),
            ("Article", Article),
            ("Tag", Tag),
            ("ArticleComment", ArticleComment),
            ("BreakingNews", BreakingNews),
            ("HomePagePlacement", HomePagePlacement),
            ("Amenity", Amenity),
            ("Hotel", Hotel),
            ("HotelRoom", HotelRoom),
            ("HotelGallery", HotelGallery),
            ("HotelNearbyPlace", HotelNearbyPlace),
            ("VideoItem", VideoItem),
            ("PhotoStory", PhotoStory),
            ("PopupAd", PopupAd),
        ]
        for label, model in models:
            self.stdout.write(f"  {label}: {model.objects.count()}")
