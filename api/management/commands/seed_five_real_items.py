import os
import shutil
import urllib.request
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds at least 5 real items with real imagery and rich bilingual content across all tables."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("=== Starting Seeding of 5 Real Items per Table ==="))
        
        self.media_root = settings.MEDIA_ROOT
        
        # Dynamically resolve frontend images directory
        frontend_candidates = [
            os.path.abspath(os.path.join(settings.BASE_DIR, '..', 'news', 'public', 'images')),
            os.path.abspath(os.path.join(settings.BASE_DIR, 'public', 'images')),
            "/home/jeevan/DEV/news-full/news/public/images"
        ]
        self.frontend_images = next((p for p in frontend_candidates if os.path.exists(p)), frontend_candidates[0])
        
        # 0. Auto-seed foundational lookup tables (districts, categories, amenities, etc.) if empty
        from apps.districts.models import District
        from apps.articles.models import Category
        from django.core.management import call_command

        if District.objects.count() == 0 or Category.objects.count() == 0:
            self.stdout.write(self.style.NOTICE("Foundational data missing. Auto-seeding minimum foundational data first..."))
            call_command('seed_minimum_foundational_data')
        
        self.setup_directories()
        self.download_and_copy_assets()
        
        self.seed_users_and_profiles()
        self.seed_authors()
        self.seed_articles_and_related()
        self.seed_hotels_and_related()
        self.seed_products_and_producers()
        self.seed_yatayat()
        self.seed_multimedia()
        self.seed_video_interactions()
        self.seed_ads()
        self.seed_districts_partners_and_sliders()
        self.seed_submissions()
        self.seed_common()
        
        self.stdout.write(self.style.SUCCESS("=== Successfully Seeded 5 Real Items Across All Tables! ==="))

    def setup_directories(self):
        dirs = [
            'authors', 'products', 'producers', 'articles', 'hero_slides',
            'banner_ads', 'popup_ads', 'yatayat', 'photo_stories', 'partners',
            'districts/slider', 'hotels/hero', 'hotels/rooms', 'hotels/gallery',
            'contributions/photos', 'contributions/stories'
        ]
        for d in dirs:
            os.makedirs(os.path.join(self.media_root, d), exist_ok=True)

    def download_url(self, url, dest_rel_path):
        dest_abs = os.path.join(self.media_root, dest_rel_path)
        if os.path.exists(dest_abs) and os.path.getsize(dest_abs) > 5000:
            return dest_rel_path
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=12) as response, open(dest_abs, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
            self.stdout.write(f"  Downloaded: {dest_rel_path}")
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"  Could not download {url}: {e}"))
            if not os.path.exists(dest_abs) or os.path.getsize(dest_abs) == 0:
                os.makedirs(os.path.dirname(dest_abs), exist_ok=True)
                seed_fallback = os.path.join(self.media_root, "seed", "articles", "articles-001.jpg")
                if os.path.exists(seed_fallback):
                    shutil.copy(seed_fallback, dest_abs)
        return dest_rel_path

    def copy_file(self, src_abs, dest_rel_path):
        dest_abs = os.path.join(self.media_root, dest_rel_path)
        os.makedirs(os.path.dirname(dest_abs), exist_ok=True)
        if os.path.exists(src_abs):
            shutil.copy(src_abs, dest_abs)
            return dest_rel_path
        elif not os.path.exists(dest_abs):
            basename = os.path.basename(src_abs)
            candidate_paths = [
                os.path.join(self.media_root, "districts", basename),
                os.path.join(self.media_root, "districts", "slider", basename),
                os.path.join(self.media_root, "places", basename),
                os.path.join(self.media_root, "seed", "articles", "articles-001.jpg"),
                os.path.join(self.media_root, "seed", "places", "places-001.jpg"),
            ]
            for cand in candidate_paths:
                if os.path.exists(cand):
                    shutil.copy(cand, dest_abs)
                    return dest_rel_path
        return dest_rel_path

    def download_and_copy_assets(self):
        self.stdout.write("Gathering real photography and media assets...")

        # Copy existing local assets
        self.copy_file(f"{self.frontend_images}/places/khaptad_national_park.jpg", "articles/khaptad_plateau.jpg")
        self.copy_file(f"{self.frontend_images}/karnali_bridge.jpg", "articles/karnali_corridor.jpg")
        self.copy_file(f"{self.frontend_images}/places/dodhara_chandani.jpg", "articles/dodhara_trade.jpg")
        self.copy_file(f"{self.frontend_images}/places/api_himal.jpg", "articles/api_nampa.jpg")
        self.copy_file(f"{self.frontend_images}/places/baidyanath_achham.jpg", "articles/baidyanath_dham.jpg")

        self.copy_file(f"{self.frontend_images}/places/khaptad_national_park.jpg", "hero_slides/khaptad_hero.jpg")
        self.copy_file(f"{self.frontend_images}/karnali_bridge.jpg", "hero_slides/karnali_hero.jpg")
        self.copy_file(f"{self.frontend_images}/places/dodhara_chandani.jpg", "hero_slides/dodhara_hero.jpg")
        self.copy_file(f"{self.frontend_images}/places/api_himal.jpg", "hero_slides/api_hero.jpg")
        self.copy_file(f"{self.frontend_images}/places/surma_sarovar.jpg", "hero_slides/surma_hero.jpg")

        self.copy_file(f"{self.frontend_images}/yatayat/bus_achham.jpg", "yatayat/bus_achham.jpg")
        self.copy_file(f"{self.frontend_images}/yatayat/bus_dolphin.jpg", "yatayat/bus_dolphin.jpg")
        self.copy_file(f"{self.frontend_images}/yatayat/hiace_van.jpg", "yatayat/hiace_van.jpg")
        self.copy_file(f"{self.frontend_images}/yatayat/jeep_bolero.jpg", "yatayat/jeep_bolero.jpg")
        self.copy_file(f"{self.frontend_images}/yatayat/bus_safal.jpg", "yatayat/bus_safal.jpg")

        self.copy_file(f"{self.frontend_images}/ads/telecom_5g_banner.jpg", "banner_ads/telecom_5g.jpg")
        self.copy_file(f"{self.frontend_images}/ads/bank_sidebar_ad.jpg", "banner_ads/bank_sidebar.jpg")
        self.copy_file(f"{self.frontend_images}/ads/university_banner.jpg", "banner_ads/university_leaderboard.jpg")
        self.copy_file(f"{self.frontend_images}/ads/tourism_banner.jpg", "banner_ads/tourism_billboard.jpg")
        self.copy_file(f"{self.frontend_images}/ads/roadblock_yeti_ad.jpg", "banner_ads/roadblock_ad.jpg")

        # Real authors headshots
        self.download_url("https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=500&q=80", "authors/sarita_chaudhary.jpg")
        self.download_url("https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500&q=80", "authors/jeevan_joshi.jpg")
        self.download_url("https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=500&q=80", "authors/prakash_bhatt.jpg")
        self.download_url("https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=500&q=80", "authors/sunita_thapa.jpg")
        self.download_url("https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=500&q=80", "authors/narendra_rawat.jpg")

        # Real products photography
        self.download_url("https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=800&q=80", "products/bajura_apples.jpg")
        self.download_url("https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=800&q=80", "products/darchula_honey.jpg")
        self.download_url("https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=800&q=80", "products/dadeldhura_timur.jpg")
        self.download_url("https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?w=800&q=80", "products/doti_khoya_peda.jpg")
        self.download_url("https://images.unsplash.com/photo-1606760227091-3dd870d97f1d?w=800&q=80", "products/baitadi_thulma.jpg")

        # Real producers portraits
        self.download_url("https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&q=80", "producers/ram_chaudhary.jpg")
        self.download_url("https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=400&q=80", "producers/keshab_joshi.jpg")
        self.download_url("https://images.unsplash.com/photo-1580489944761-15a19d654956?w=400&q=80", "producers/parbati_bohara.jpg")
        self.download_url("https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=400&q=80", "producers/dhan_singh_dhami.jpg")
        self.download_url("https://images.unsplash.com/photo-1567532939604-b6b5b0db2604?w=400&q=80", "producers/shanti_devi.jpg")

        # Photo stories
        self.copy_file(f"{self.frontend_images}/places/khaptad_national_park.jpg", "photo_stories/story_khaptad.jpg")
        self.copy_file(f"{self.frontend_images}/places/surma_sarovar.jpg", "photo_stories/story_surma.jpg")
        self.copy_file(f"{self.frontend_images}/places/tikapur_park.jpg", "photo_stories/story_tikapur.jpg")
        self.copy_file(f"{self.frontend_images}/ghodaghodi_lake.jpg", "photo_stories/story_ghodaghodi.jpg")
        self.copy_file(f"{self.frontend_images}/places/ugratara_temple.jpg", "photo_stories/story_ugratara.jpg")

        # Contribution community photos
        self.copy_file(f"{self.frontend_images}/places/khaptad_national_park.jpg", "contributions/photos/khaptad_mist.jpg")
        self.copy_file(f"{self.frontend_images}/places/tikapur_park.jpg", "contributions/photos/shuklaphanta_herd.jpg")
        self.copy_file(f"{self.frontend_images}/karnali_bridge.jpg", "contributions/photos/karnali_bridge_view.jpg")
        self.copy_file(f"{self.frontend_images}/places/api_himal.jpg", "contributions/photos/api_glow.jpg")
        self.copy_file(f"{self.frontend_images}/places/ugratara_temple.jpg", "contributions/photos/amargadhi_fort_view.jpg")

        # Hotel hero, room, and gallery assets fallback
        hotel_asset_mappings = [
            ("hotels/hero/hotel_hero_1.jpg", "seed/hotels/hotels-001.jpg"),
            ("hotels/hero/hotel_hero_3.jpg", "seed/hotels/hotels-002.jpg"),
            ("hotels/hero/hotel_hero_4.jpg", "seed/hotels/hotels-003.jpg"),
            ("hotels/hero/hotel_hero_6.jpg", "seed/hotels/hotels-004.jpg"),
            ("hotels/hero/hotel_hero_8.jpg", "seed/hotels/hotels-005.jpg"),
            ("hotels/rooms/room_5.jpg", "seed/hotel-rooms/hotel-rooms-001.jpg"),
            ("hotels/rooms/room_6.jpg", "seed/hotel-rooms/hotel-rooms-002.jpg"),
            ("hotels/rooms/room_7.jpg", "seed/hotel-rooms/hotel-rooms-003.jpg"),
            ("hotels/rooms/room_8.jpg", "seed/hotel-rooms/hotel-rooms-004.jpg"),
            ("hotels/gallery/gallery_local_24_1.jpg", "seed/hotel-gallery/hotel-gallery-001.jpg"),
            ("hotels/gallery/gallery_local_17_2.jpg", "seed/hotel-gallery/hotel-gallery-002.jpg"),
            ("hotels/gallery/gallery_local_23_4.jpg", "seed/hotel-gallery/hotel-gallery-003.jpg"),
            ("hotels/gallery/gallery_local_15_3.jpg", "seed/hotel-gallery/hotel-gallery-004.jpg"),
            ("hotels/gallery/gallery_local_14_2.jpg", "seed/hotel-gallery/hotel-gallery-005.jpg"),
        ]
        for dest, src in hotel_asset_mappings:
            dest_abs = os.path.join(self.media_root, dest)
            if not os.path.exists(dest_abs):
                src_abs = os.path.join(self.media_root, src)
                if os.path.exists(src_abs):
                    os.makedirs(os.path.dirname(dest_abs), exist_ok=True)
                    shutil.copy(src_abs, dest_abs)

    def seed_users_and_profiles(self):
        from apps.accounts.models import UserProfile
        
        users_data = [
            ("editor_kailali", "editor1@sudur.com", "Jeevan", "Joshi", "9858400001", "Senior Regional Editor based in Dhangadhi."),
            ("reporter_achham", "reporter1@sudur.com", "Sarita", "Chaudhary", "9858400002", "Investigative Field Reporter covering Achham & Doti."),
            ("tech_admin", "tech@sudur.com", "Prakash", "Bhatt", "9858400003", "Platform Systems Architect."),
            ("correspondent_darchula", "darchula.news@sudur.com", "Dhan", "Dhami", "9858400004", "Northern Border & High Altitude Mountain Correspondent."),
            ("culture_writer_dadeldhura", "culture@sudur.com", "Sunita", "Thapa", "9858400005", "Heritage and Indigenous Deuda Arts Columnist.")
        ]
        for uname, email, fname, lname, phone, bio in users_data:
            u, _ = User.objects.get_or_create(
                username=uname,
                defaults={'email': email, 'first_name': fname, 'last_name': lname, 'is_staff': True}
            )
            u.set_password('Admin123!')
            u.save()
            UserProfile.objects.update_or_create(
                user=u,
                defaults={'phone': phone}
            )
        self.stdout.write(f"  accounts.UserProfile: {UserProfile.objects.count()} items")

    def seed_authors(self):
        from apps.articles.models import Author
        
        authors = [
            ("jeevan-joshi", "Jeevan Joshi", "जीवन जोशी", "Chief Editor & Investigative Journalist", "प्रधान सम्पादक तथा खोज पत्रकार", "Senior political analyst with 15 years experience covering Sudurpashchim province.", "सुदूरपश्चिम प्रदेशको राजनीति र विकास पत्रकारितामा १५ वर्षको अनुभव।", "authors/jeevan_joshi.jpg", "Kailali"),
            ("sarita-chaudhary", "Sarita Chaudhary", "सरिता चौधरी", "Senior Provincial Reporter", "वरिष्ठ प्रदेश संवाददाता", "Specializes in indigenous Tharu culture, agriculture, and rural economy.", "थारु संस्कृति, कृषि र ग्रामीण अर्थतन्त्रमा विशेष दख्खल राख्ने पत्रकार।", "authors/sarita_chaudhary.jpg", "Kanchanpur"),
            ("prakash-bhatt", "Prakash Bhatt", "प्रकाश भट्ट", "Himalayan Tourism & Ecology Correspondent", "हिमाल तथा पर्यटन संवाददाता", "Passionate trekker and writer covering Api Himal, Saipal, and Khaptad trails.", "अपि, सैपाल र खप्तड क्षेत्रको पर्यटन तथा पर्यावरण संरक्षण लेखक।", "authors/prakash_bhatt.jpg", "Darchula"),
            ("sunita-thapa", "Sunita Thapa", "सुनिता थापा", "Education & Social Affairs Writer", "शिक्षा तथा सामाजिक सरोकार स्तम्भकार", "Documenting women leadership and rural public school education across hill districts.", "पहाडी जिल्लाका सार्वजनिक शिक्षा र महिला सशक्तीकरण विषयक स्तम्भकार।", "authors/sunita_thapa.jpg", "Dadeldhura"),
            ("narendra-rawat", "Narendra Rawat", "नरेन्द्र रावत", "Economic & Infrastructure Analyst", "आर्थिक तथा पूर्वाधार विश्लेषक", "Tracking cross-border trade, roads, and hydropower developments in Province 7.", "सुदूरपश्चिमका जलविद्युत्, सडक सञ्जाल र सीमा व्यापारका विश्लेषक।", "authors/narendra_rawat.jpg", "Bajhang"),
        ]

        for slug, n_en, n_ne, r_en, r_ne, b_en, b_ne, av, dist in authors:
            Author.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': n_en, 'name_en': n_en, 'name_ne': n_ne,
                    'role': r_en, 'role_en': r_en, 'role_ne': r_ne,
                    'bio': b_en, 'bio_en': b_en, 'bio_ne': b_ne,
                    'avatar': f"/media/{av}",
                    'district': dist
                }
            )
        self.stdout.write(f"  articles.Author: {Author.objects.count()} items")

    def seed_articles_and_related(self):
        from apps.articles.models import (
            Article, Author, Category, Tag, ArticleComment,
            BreakingNews, HomePagePlacement, HeroSlide, ArticleBookmark
        )
        from apps.districts.models import District

        authors = list(Author.objects.all().order_by('id'))
        cat_news = Category.objects.filter(slug='news').first()
        cat_politics = Category.objects.filter(slug='politics').first()
        cat_tourism = Category.objects.filter(slug='tourism').first()
        cat_economy = Category.objects.filter(slug='economy').first()
        cat_culture = Category.objects.filter(slug='culture').first()

        dist_kailali = District.objects.filter(slug='kailali').first()
        dist_doti = District.objects.filter(slug='doti').first()
        dist_kanchanpur = District.objects.filter(slug='kanchanpur').first()
        dist_darchula = District.objects.filter(slug='darchula').first()
        dist_achham = District.objects.filter(slug='achham').first()

        articles_data = [
            (
                "khaptad-tourism-corridor-expansion-2026",
                "Khaptad National Park Opens New Eco-Tourism Trekking Corridor for Himalayan Travelers",
                "खप्तड राष्ट्रिय निकुञ्जमा नयाँ पर्यावरण-पर्यटन पदमार्ग विस्तार, पदयात्रीहरूको आकर्षण बढ्दो",
                "The pristine 225 sq km plateau of Khaptad sees an upgrade in solar-powered eco-lodges and sustainable nature trails across Doti and Bajhang.",
                "खप्तडको सुन्दर २२५ वर्ग किमी घाँसे मैदान र त्रिवेणी धाम जोड्ने नयाँ पदमार्ग तथा सौर्य ऊर्जा युक्त होमस्टेहरू सञ्चालनमा आएका छन्।",
                "# Sustainable Tourism in Khaptad Plateau\n\nKhaptad National Park, known as the living meditation haven of Khaptad Baba, is witnessing a sustainable tourism renaissance. With over 22 sweeping meadows (patans) and rare medicinal herbs, local municipalities in Doti, Achham, and Bajhang have collaborated to establish eco-friendly trail markers and waste-neutral camping spots.\n\nAccording to Park Wardens, the number of international and domestic trekkers has doubled this autumn, providing vital seasonal income to indigenous host communities.",
                "# खप्तड पठारमा दिगो पर्यटनको नयाँ आयाम\n\nखप्तड राष्ट्रिय निकुञ्जमा २२ वटा विशाल पाटन (घाँसे मैदान) र ५६७ प्रजातिका वनस्पतिहरू संरक्षण गरिएका छन्। डोटी, अछाम, बझाङ र बाजुराको संगम स्थल मानिने यस क्षेत्रमा हालै सौर्य ऊर्जा र काठबाट निर्मित पर्यावरण-मैत्री लजहरू थपिएका छन्।\n\nपर्यटन व्यवसायीहरूका अनुसार चालू सिजनमा आन्तरिक तथा बाह्य पर्यटकहरूको आगमन उल्लेख्य रूपमा बढेको छ।",
                "articles/khaptad_plateau.jpg",
                "Khaptad National Park Meadows during autumn bloom",
                "शरद ऋतुमा खप्तड राष्ट्रिय निकुञ्जका मनोरम पाटनहरू",
                cat_tourism, authors[2] if len(authors) > 2 else authors[0], dist_doti, True, True
            ),
            (
                "karnali-economic-corridor-trade-link-complete",
                "Karnali River Corridor Connectivity Boosts Inter-Provincial Trade and Transit",
                "कर्णाली आर्थिक करिडोर सञ्चालनमा: सुदूरपश्चिम र कर्णालीबीचको व्यापारमा ऐतिहासिक फड्को",
                "New all-weather dual-lane bridges along the Karnali highway connect Dhangadhi trade hub directly to Surkhet and the northern highlands.",
                "कर्णाली नदी किनार हुँदै सुदूरपश्चिमका मुख्य सहर र हिमाली जिल्ला जोड्ने व्यापारिक मार्ग पूर्ण रूपमा स्तरोन्नति भएको छ।",
                "# Transforming Regional Commerce via Karnali Corridor\n\nThe completion of key asphalt road segments along the Karnali arterial highway marks a landmark victory for regional supply chains. Agricultural produce from Achham and Bajura can now reach Dhangadhi's wholesale markets in under 8 hours.\n\nTransport federations report reduced freight costs by 28%, significantly lowering the retail price of fresh organic grains and fruits in lowland urban centers.",
                "# कर्णाली करिडोरले जोडेको अन्तर-प्रादेशिक अर्थतन्त्र\n\nकैलालीको चिसापानी कर्णाली पुलदेखि पहाडी जिल्लाहरू जोड्ने द्रुतमार्ग कालोपत्रे भएसँगै ढुवानी समय र खर्च उल्लेख्य घटेको छ। अछाम र बाजुराका किसानहरूले उत्पादन गरेका जैविक फलफूल र दालहरू अब सोझै तराईका बजारसम्म सहजै पुग्ने भएका छन्।",
                "articles/karnali_corridor.jpg",
                "Iconic Karnali Bridge and transportation corridor",
                "कर्णाली नदीको विशाल पुल तथा व्यापारिक मार्ग",
                cat_economy, authors[0], dist_kailali, True, False
            ),
            (
                "dodhara-chandani-dry-port-cross-border-breakthrough",
                "Dodhara Chandani Dry Port Construction Accelerates Nepal-India Strategic Trade",
                "दोधारा चाँदनी सुक्खा बन्दरगाह निर्माण तीव्र: नेपाल-भारत अन्तर्राष्ट्रिय व्यापारको नयाँ ढोका",
                "The multi-billion rupee dry port and integrated check post in Kanchanpur gears up to become western Nepal's largest freight transit gateway.",
                "कञ्चनपुरमा निर्माणाधीन दोधारा चाँदनी सुक्खा बन्दरगाहले पश्चिमी नेपालको आर्थिक मुहार फेर्ने अपेक्षा गरिएको छ।",
                "# A New International Trade Hub in the Far-West\n\nStrategically located near the Mahakali River, the Dodhara Chandani Dry Port will offer direct rail and highway links to major Indian industrial corridors in New Delhi and Uttar Pradesh.\n\nCustoms automation, quarantine labs, and container freight stations are currently 65% complete, positioning Sudurpashchim as an attractive destination for foreign joint ventures.",
                "# दोधारा चाँदनी बन्दरगाहबाट पश्चिम नेपालको आर्थिक रूपान्तरण\n\nमहाकाली पारीको दोधारा चाँदनीमा निर्माण भइरहेको सुक्खा बन्दरगाहले भारतको राजधानी नयाँ दिल्लीसँग नेपालको सबैभन्दा छोटो व्यापारिक दूरी स्थापित गर्नेछ। यस आयोजनाबाट हजारौं रोजगारी सृजना हुने विश्वास लिइएको छ।",
                "articles/dodhara_trade.jpg",
                "Dodhara Chandani suspension connectivity and project site",
                "दोधारा चाँदनी क्षेत्र तथा सुक्खा बन्दरगाह निर्माण स्थल",
                cat_politics, authors[1] if len(authors) > 1 else authors[0], dist_kanchanpur, False, True
            ),
            (
                "api-nampa-conservation-snow-leopard-census-2026",
                "Api Nampa Conservation Area Records Healthiest Snow Leopard Population in Decades",
                "अपि नाम्पा संरक्षण क्षेत्रमा हिउँ चितुवाको संख्या वृद्धि: जैविक विविधता संरक्षणमा ऐतिहासिक उपलब्धि",
                "Camera traps across Darchula's glacial valleys confirm an increase in snow leopard families, signaling a flourishing high-altitude ecosystem.",
                "दार्चुलाको उच्च हिमाली भेगमा दुर्लभ हिउँ चितुवाको संख्यामा उत्साहजनक वृद्धि देखिएको वन्यजन्तु संरक्षण टोलीले जनाएको छ।",
                "# Wildlife Success in the Shadows of Mt. Api\n\nCovering steep terrain from subtropical forests to 7,132-meter peaks, Api Nampa Conservation Area is one of the most biodiverse preserves in the Himalayas. High-definition sensor cameras installed by community forest groups captured multiple breeding pairs of snow leopards and blue sheep.\n\nCommunity anti-poaching units have been lauded by provincial authorities for safeguarding this fragile alpine habitat.",
                "# अपि हिमालको काखमा हिउँ चितुवाको सफल संरक्षण\n\nदार्चुलाको अपि नाम्पा क्षेत्रमा राखिएका स्वचालित क्यामराहरूमा हिउँ चितुवाका स्वस्थ बथानहरू कैद भएका छन्। स्थानीय युवाहरूको समुदाय-आधारित संरक्षण दस्ताले चोरी सिकारी नियन्त्रणमा महत्वपूर्ण योगदान पुर्‍याएको छ।",
                "articles/api_nampa.jpg",
                "The glacial peaks of Mt. Api in Darchula",
                "दार्चुलास्थित अपि हिमाल तथा संरक्षण क्षेत्र",
                cat_news, authors[2] if len(authors) > 2 else authors[0], dist_darchula, False, False
            ),
            (
                "baidyanath-dham-heritage-temple-restoration",
                "Historic Baidyanath Dham in Achham Undergoes Archaeological Preservation",
                "अछामको ऐतिहासिक बैद्यनाथ धामको संरक्षण तथा जीर्णोद्धार कार्य सम्पन्न",
                "Centuries-old stone temples along the sacred confluence of Budhi Ganga and Saraswati rivers are restored using authentic Vedic masonry techniques.",
                "अछामस्थित चार धाममध्येको एक पवित्र बैद्यनाथ क्षेत्रको प्राचीन ढुङ्गे मन्दिर तथा कलाकृतिहरूको पुरातत्विक संरक्षण गरिएको छ।",
                "# Restoring Far-West Nepal's Spiritual Crown Jewel\n\nBaidyanath Dham in Achham is renowned in ancient Puranic texts as a revered pilgrimage site for wellness and meditation. Led by the Department of Archaeology, master craftsmen repaired natural stone carvings and renovated river bathing ghats without altering the centuries-old traditional architecture.\n\nThe annual Shivaratri festival is set to accommodate over 50,000 pilgrims with modern sanitation and riverside pathways.",
                "# पवित्र बैद्यनाथ क्षेत्रको पुरातात्विक पुनरुत्थान\n\nबुढीगंगा नदीको किनारमा अवस्थित अछामको बैद्यनाथ धाम धार्मिक तथा सांस्कृतिक दृष्टिकोणले अत्यन्त महत्वपूर्ण छ। प्राचीन कला र शैलीलाई अक्षुण्ण राख्दै मन्दिर, धर्मशाला र स्नान घाटहरूको जीर्णोद्धार गरिएको छ।",
                "articles/baidyanath_dham.jpg",
                "The sacred shrine of Baidyanath Dham in Achham",
                "अछामको ऐतिहासिक बैद्यनाथ मन्दिर तथा पवित्र नदी तट",
                cat_culture, authors[3] if len(authors) > 3 else authors[0], dist_achham, False, False
            ),
        ]

        created_articles = []
        for slug, t_en, t_ne, ex_en, ex_ne, c_en, c_ne, img, cap_en, cap_ne, cat, aut, dist, feat, brk in articles_data:
            art, _ = Article.objects.update_or_create(
                slug=slug,
                defaults={
                    'title': t_en, 'title_en': t_en, 'title_ne': t_ne,
                    'excerpt': ex_en, 'excerpt_en': ex_en, 'excerpt_ne': ex_ne,
                    'content': c_en, 'content_en': c_en, 'content_ne': c_ne,
                    'image': img,
                    'featuredImage': f"/media/{img}",
                    'imageCaption': cap_en, 'imageCaption_en': cap_en, 'imageCaption_ne': cap_ne,
                    'meta_title': t_en, 'meta_title_en': t_en, 'meta_title_ne': t_ne,
                    'meta_description': ex_en, 'meta_description_en': ex_en, 'meta_description_ne': ex_ne,
                    'category': cat,
                    'author': aut,
                    'district': dist,
                    'status': 'published',
                    'featured': feat,
                    'breaking': brk,
                    'popular': True,
                    'readTime': 5,
                    'views': 1240,
                    'likes': 88,
                    'publishedAt': timezone.now()
                }
            )
            created_articles.append(art)
        self.stdout.write(f"  articles.Article: {Article.objects.count()} items")

        # Tags
        tags_list = ["सुदूरपश्चिम", "पर्यटन", "पूर्वाधार", "अर्थतन्त्र", "वातावरण", "संस्कृति"]
        Tag.objects.all().delete()
        for idx, tname in enumerate(tags_list):
            target_art = created_articles[idx % len(created_articles)]
            Tag.objects.create(name=tname, article=target_art)
        self.stdout.write(f"  articles.Tag: {Tag.objects.count()} items")

        # Article Comments
        comments_data = [
            ("Madan Bhandari", "Dhangadhi", "Very insightful coverage of the Karnali trade corridor. This road is truly a lifeline!"),
            ("Rekha Sharma", "Mahendranagar", "Dodhara Chandani dry port will change the destiny of our youth. Great reporting."),
            ("Deepak Bohara", "Dipayal", "Khaptad needs more eco-friendly homestays just like mentioned. Proud of our province!"),
            ("Ganesh Rawat", "Chainpur", "Snow leopard conservation in Api Nampa is great news for global biodiversity enthusiasts."),
            ("Bimala Joshi", "Sanfebagar", "Baidyanath Dham restoration was long overdue. Appreciate the detailed history!")
        ]
        ArticleComment.objects.all().delete()
        for idx, (aname, aloc, cont) in enumerate(comments_data):
            art = created_articles[idx % len(created_articles)]
            ArticleComment.objects.create(
                article=art, authorName=aname, authorLocation=aloc, content=cont, likes=12
            )
        self.stdout.write(f"  articles.ArticleComment: {ArticleComment.objects.count()} items")

        # Breaking News
        breaking_items = [
            ("Special Provincial Assembly session convenes in Dhangadhi to approve major tourism corridor budgets.", "सुदूरपश्चिम प्रदेश सभाको विशेष बैठक सुरु, पर्यटकीय करिडोरका लागि विशेष बजेट पारित।"),
            ("Karnali bridge dual-lane expansion opens ahead of schedule for commercial freight traffic.", "कर्णाली पुल दोहोरो लेन स्तरोन्नति सम्पन्न, व्यावसायिक सवारी साधन सञ्चालनमा।"),
            ("Organic apple harvesting begins in Bajura with direct delivery routes to Kailali markets.", "बाजुराका उच्च हिमाली बगैँचाबाट स्याउ संकलन सुरु, तराईका बजारमा सोझै ढुवानी।"),
            ("New immigration and trade terminal operational at Dodhara Chandani border checkpoint.", "दोधारा चाँदनी सुक्खा बन्दरगाह क्षेत्रमा नयाँ व्यापारिक टर्मिनल सञ्चालनमा।"),
            ("Eco-tourism festival announced at Khaptad Triveni Dham for the upcoming full moon week.", "खप्तड त्रिवेणी धाममा आउँदो पूर्णिमाका दिन वृहत् पर्यावरण पर्यटन महोत्सव आयोजना हुने।")
        ]
        BreakingNews.objects.all().delete()
        for idx, (t_en, t_ne) in enumerate(breaking_items):
            art = created_articles[idx % len(created_articles)]
            BreakingNews.objects.create(
                text=t_en, text_en=t_en, text_ne=t_ne,
                href=f"/article/{art.slug}"
            )
        self.stdout.write(f"  articles.BreakingNews: {BreakingNews.objects.count()} items")

        # Hero Slides
        slides_data = [
            ("Khaptad Plateau: Where Nature Meets Solitude", "खप्तडको अनुपम प्राकृतिक सौन्दर्य", "Eco-Tourism", "पर्यावरण पर्यटन", "articles/khaptad_plateau.jpg", created_articles[0]),
            ("Karnali Highway: Arterial Vein of the West", "कर्णाली करिडोर: पश्चिमको समृद्धिको आधार", "Infrastructure", "पूर्वाधार", "articles/karnali_corridor.jpg", created_articles[1]),
            ("Dodhara Chandani: Cross-Border Strategic Hub", "दोधारा चाँदनी: नयाँ अन्तर्राष्ट्रिय व्यापार केन्द्र", "Trade & Commerce", "व्यापार", "articles/dodhara_trade.jpg", created_articles[2]),
            ("Mt. Api Glaciers: Sanctuary of the Snow Leopard", "अपि हिमालको काखमा दुर्लभ जैविक विविधता", "Wildlife", "वन्यजन्तु", "articles/api_nampa.jpg", created_articles[3]),
            ("Baidyanath Dham: Millennia of Sacred Architecture", "बैद्यनाथ धाम: शताब्दीऔं पुरानो सांस्कृतिक सम्पदा", "Heritage", "धार्मिक सम्पदा", "articles/baidyanath_dham.jpg", created_articles[4])
        ]
        HeroSlide.objects.all().delete()
        for idx, (t_en, t_ne, sub_en, sub_ne, img, art) in enumerate(slides_data):
            HeroSlide.objects.create(
                title=t_en, title_en=t_en, title_ne=t_ne,
                subtitle=sub_en, subtitle_en=sub_en, subtitle_ne=sub_ne,
                excerpt=art.excerpt_en, excerpt_en=art.excerpt_en, excerpt_ne=art.excerpt_ne,
                image=img,
                image_url=f"/media/{img}",
                article=art,
                order=idx + 1,
                is_active=True,
                primary_button_text_en="Read Full Story",
                primary_button_text_ne="पूरा पढ्नुहोस्",
                primary_button_url=f"/article/{art.slug}"
            )
        self.stdout.write(f"  articles.HeroSlide: {HeroSlide.objects.count()} items")

        # HomePage Placements
        placements = [
            "Lead Story (मुख्य समाचार)",
            "Editor's Choice (सम्पादकीय रोजाइ)",
            "Trending Wire (चर्चित विषय)",
            "Provincial Focus (प्रदेश विशेष)",
            "Deep Dive Dispatch (विस्तृत खोज)"
        ]
        HomePagePlacement.objects.all().delete()
        for sname in placements:
            hp = HomePagePlacement.objects.create(section_name=sname)
            hp.articles.set(created_articles)
        self.stdout.write(f"  articles.HomePagePlacement: {HomePagePlacement.objects.count()} items")

        # Article Bookmarks
        admin_user = User.objects.filter(is_superuser=True).first()
        ArticleBookmark.objects.all().delete()
        if admin_user:
            for art in created_articles:
                ArticleBookmark.objects.create(user=admin_user, article=art)
        self.stdout.write(f"  articles.ArticleBookmark: {ArticleBookmark.objects.count()} items")

    def seed_hotels_and_related(self):
        from apps.hotels.models import Hotel, HotelRoom, HotelGallery, HotelNearbyPlace, Amenity
        from apps.articles.models import Category
        from apps.districts.models import District

        cat_stay = Category.objects.filter(slug='stay').first()
        dist_kailali = District.objects.filter(slug='kailali').first()
        dist_doti = District.objects.filter(slug='doti').first()
        dist_kanchanpur = District.objects.filter(slug='kanchanpur').first()
        dist_darchula = District.objects.filter(slug='darchula').first()
        dist_dadeldhura = District.objects.filter(slug='dadeldhura').first()

        amenities = list(Amenity.objects.all())

        hotels_data = [
            (
                "hotel-rubus-dhangadhi",
                "Hotel Rubus Dhangadhi",
                "Boutique Luxury Hotel",
                dist_kailali,
                "Main Road, Hasanpur, Dhangadhi",
                "Dhangadhi Sub-Metropolitan City",
                "28.6852", "80.5983",
                4.8, 142,
                "hotels/hero/hotel_hero_1.jpg",
                "Premier 4-star boutique hotel in the heart of Dhangadhi with rooftop swimming pool and conference halls.",
                "Hotel Rubus offers state-of-the-art hospitality in Kailali, featuring elegant rooms, international fine dining, and seamless airport shuttle transfers.",
                "091-523456", "9858421000", "info@hotelrubus.com", "https://hotelrubus.com"
            ),
            (
                "khaptad-camp-resort",
                "Khaptad Eco Camp & Resort",
                "Highland Eco Resort",
                dist_doti,
                "Near Triveni Dham, Khaptad Plateau",
                "Silgadhi Municipality",
                "29.3524", "81.0254",
                4.9, 98,
                "hotels/hero/hotel_hero_3.jpg",
                "Authentic mountain resort situated near the serene meadows of Khaptad National Park with traditional wooden chalets.",
                "Experience the peaceful magic of Khaptad with heated organic herbal baths, locally sourced highland meals, and guided meditation walks.",
                "094-420111", "9858455222", "stay@khaptadcamp.com", "https://khaptadcamp.com"
            ),
            (
                "shuklaphanta-jungle-lodge",
                "Shuklaphanta Jungle Lodge",
                "Wildlife Safari Lodge",
                dist_kanchanpur,
                "Majhgaun, Near Park Gate, Mahendranagar",
                "Bhimdatta Municipality",
                "28.9167", "80.1833",
                4.7, 115,
                "hotels/hero/hotel_hero_4.jpg",
                "Eco-lodge on the edge of Shuklaphanta National Park, ideal for swamp deer watching and elephant safaris.",
                "Immerse yourself in nature with our spacious thatched-roof cottages, naturalist guides, and peaceful sunset decks overlooking wetlands.",
                "099-521999", "9858711888", "safari@shuklalodge.com", "https://shuklalodge.com"
            ),
            (
                "devbhoomi-heritage-resort",
                "Devbhoomi Heritage Resort",
                "Cultural Hilltop Resort",
                dist_dadeldhura,
                "Amargadhi Fort Road, Dadeldhura",
                "Amargadhi Municipality",
                "29.3000", "80.5833",
                4.6, 76,
                "hotels/hero/hotel_hero_6.jpg",
                "Panoramic hilltop retreat overlooking the sacred Mahakali basin and historic Amargadhi Fort.",
                "Designed with traditional stone architecture of western Nepal, Devbhoomi provides cozy mountain cottages and authentic organic Kumaoni-Nepali gastronomy.",
                "096-410222", "9858833444", "welcome@devbhoomiresort.com", "https://devbhoomiresort.com"
            ),
            (
                "api-view-hotel-darchula",
                "Api View Hotel & Alpine Lodge",
                "Alpine Transit Hotel",
                dist_darchula,
                "Main Bazaar, Khalanga",
                "Mahakali Municipality",
                "29.8400", "80.5333",
                4.5, 62,
                "hotels/hero/hotel_hero_8.jpg",
                "Cozy basecamp hotel for mountaineers and pilgrims heading toward Api Himal and the Kailash-Mansarovar trail.",
                "Centrally located in Khalanga, offering hot showers, high-speed WiFi, hearty Himalayan hot pots, and trusted mountain porter logistics.",
                "093-420333", "9858944555", "lodge@apiviewhotel.com", "https://apiviewhotel.com"
            ),
        ]

        Hotel.objects.all().delete()
        created_hotels = []
        for slug, name, htype, dist, addr, mun, lat, lon, rat, rev, img, sdesc, abt, p1, p2, em, web in hotels_data:
            h = Hotel.objects.create(
                slug=slug, name=name, hotel_type=htype, category=cat_stay, district=dist,
                address=addr, municipality=mun, latitude=lat, longitude=lon,
                rating=rat, reviews_count=rev, hero_image=img,
                short_description=sdesc, about=abt,
                phone1=p1, phone2=p2, email=em, website=web,
                highlights=["Free High-Speed WiFi", "Mountain View Balconies", "Organic Traditional Cuisine", "24/7 Hot Water"]
            )
            h.amenities.set(amenities[:4])
            created_hotels.append(h)
        self.stdout.write(f"  hotels.Hotel: {Hotel.objects.count()} items")

        # Hotel Rooms
        rooms_data = [
            ("Deluxe Panoramic Suite", 2, "1 King Bed", "hotels/rooms/room_5.jpg", 6500.00),
            ("Executive Twin Room", 2, "2 Single Beds", "hotels/rooms/room_6.jpg", 4800.00),
            ("Himalayan Heritage Cottage", 4, "2 Queen Beds", "hotels/rooms/room_7.jpg", 8500.00),
            ("Eco Glamping Luxury Tent", 2, "1 King Bed", "hotels/rooms/room_8.jpg", 5500.00),
            ("Standard Valley View Room", 2, "1 Queen Bed", "hotels/rooms/room_5.jpg", 3500.00),
        ]
        HotelRoom.objects.all().delete()
        for idx, (rname, gst, btype, rimg, prc) in enumerate(rooms_data):
            h = created_hotels[idx % len(created_hotels)]
            HotelRoom.objects.create(hotel=h, name=rname, guests=gst, bed_type=btype, image=rimg, price=prc)
        self.stdout.write(f"  hotels.HotelRoom: {HotelRoom.objects.count()} items")

        # Hotel Gallery
        gallery_images = [
            ("Lobby and Reception Hall", "hotels/gallery/gallery_local_24_1.jpg"),
            ("Sunset Lounge Terrace", "hotels/gallery/gallery_local_17_2.jpg"),
            ("Organic Garden Dining", "hotels/gallery/gallery_local_23_4.jpg"),
            ("Spa and Wellness Center", "hotels/gallery/gallery_local_15_3.jpg"),
            ("Conference and Event Auditorium", "hotels/gallery/gallery_local_14_2.jpg"),
        ]
        HotelGallery.objects.all().delete()
        for idx, (cap, gimg) in enumerate(gallery_images):
            h = created_hotels[idx % len(created_hotels)]
            HotelGallery.objects.create(hotel=h, image=gimg, caption=cap)
        self.stdout.write(f"  hotels.HotelGallery: {HotelGallery.objects.count()} items")

        # Nearby Places
        nearby_data = [
            ("Ghodaghodi Bird Sanctuary", "42 km"),
            ("Amargadhi Historic Fort", "1.8 km"),
            ("Shuklaphanta Swamp Deer Grasslands", "4.5 km"),
            ("Khaptad Baba Ashram & Hermitage", "2.2 km"),
            ("Mahakali River Suspension Bridge", "12 km")
        ]
        HotelNearbyPlace.objects.all().delete()
        for idx, (pname, dist_str) in enumerate(nearby_data):
            h = created_hotels[idx % len(created_hotels)]
            HotelNearbyPlace.objects.create(hotel=h, name=pname, distance=dist_str)
        self.stdout.write(f"  hotels.HotelNearbyPlace: {HotelNearbyPlace.objects.count()} items")

    def seed_products_and_producers(self):
        from apps.products.models import ProductCategory, ProductProducer, LocalProduct
        from apps.districts.models import District

        dist_kailali = District.objects.filter(slug='kailali').first()
        dist_doti = District.objects.filter(slug='doti').first()
        dist_bajura = District.objects.filter(slug='bajura').first()
        dist_dadeldhura = District.objects.filter(slug='dadeldhura').first()
        dist_darchula = District.objects.filter(slug='darchula').first()
        dist_baitadi = District.objects.filter(slug='baitadi').first()

        cat_dairy = ProductCategory.objects.filter(slug='dairy').first()
        cat_fruits = ProductCategory.objects.filter(slug='fruits').first()
        cat_spices = ProductCategory.objects.filter(slug='spices').first()
        cat_crafts = ProductCategory.objects.filter(slug='handicrafts').first()
        cat_grains = ProductCategory.objects.filter(slug='grains').first()

        producers_data = [
            ("Ram Bahadur Chaudhary", "राम बहादुर चौधरी", dist_kailali, "Hasuliya, Kailali", "हसुलिया, कैलाली", "9858411222", "Pioneer dairy cooperative leader in southern Kailali.", "कैलालीका अग्रणी दुग्ध व्यवसायी तथा सहकारी अभियन्ता।", "16 Years", "producers/ram_chaudhary.jpg"),
            ("Keshab Raj Joshi", "केशव राज जोशी", dist_bajura, "Swamikartik, Bajura", "स्वामीकार्तिक, बाजुरा", "9858522333", "Certified organic high-altitude apple farmer with 1,200 trees.", "उच्च हिमाली भेगमा जैविक स्याउ खेती गर्दै आएका अगुवा कृषक।", "14 Years", "producers/keshab_joshi.jpg"),
            ("Parbati Bohara", "पार्वती बोहरा", dist_dadeldhura, "Ajayameru, Dadeldhura", "अजयमेरु, डडेल्धुरा", "9858633444", "Forest timur and organic herbal spices cultivator.", "वन्य टिमुर र जैविक मसला उत्पादन तथा प्रशोधन विशेषज्ञ।", "11 Years", "producers/parbati_bohara.jpg"),
            ("Dhan Singh Dhami", "धन सिंह धामी", dist_darchula, "Byas Rural Municipality, Darchula", "व्यास गाउँपालिका, दार्चुला", "9858744555", "Traditional Himalayan cliff-honey collector and beekeeper.", "परम्परागत हिमाली भीर मह संकलक तथा मौरीपालक कृषक।", "22 Years", "producers/dhan_singh_dhami.jpg"),
            ("Shanti Devi B.K.", "शान्ति देवी वि.क.", dist_baitadi, "Patan Municipality, Baitadi", "पाटन नगरपालिका, बैतडी", "9858855666", "Master weaver of indigenous wool blankets (Thulma & Radi-Pakhi).", "परम्परागत उन र राडीपाखी तथा थुल्मा बुनाइका सिद्धहस्त शिल्पी।", "19 Years", "producers/shanti_devi.jpg"),
        ]

        ProductProducer.objects.all().delete()
        created_producers = []
        for name_en, name_ne, dist, addr_en, addr_ne, ph, bio_en, bio_ne, exp, av in producers_data:
            p = ProductProducer.objects.create(
                name=name_en, name_en=name_en, name_ne=name_ne,
                district=dist,
                municipality_address=addr_en, municipality_address_en=addr_en, municipality_address_ne=addr_ne,
                phone=ph,
                bio=bio_en, bio_en=bio_en, bio_ne=bio_ne,
                experience_years=exp,
                avatar=av,
                is_verified=True
            )
            created_producers.append(p)
        self.stdout.write(f"  products.ProductProducer: {ProductProducer.objects.count()} items")

        products_data = [
            (
                "doti-pure-khoya-peda",
                "Silgadhi Pure Khoya Peda",
                "डोटीको प्रख्यात शुद्ध खुवा पेडा",
                cat_dairy, dist_doti,
                "Traditional milk fudge confection prepared from grass-fed cow milk in the historic hill town of Silgadhi.",
                "डोटीको सिलगढीमा परम्परागत तरिकाले शुद्ध गाई-भैँसीको दूधबाट बनाइने स्वादिलो र पौष्टिक खुवा पेडा।",
                "Ram Bahadur Chaudhary", "9858411222", "products/doti_khoya_peda.jpg",
                "All Year", "रु. ९०० - १,०००", "kg", True
            ),
            (
                "bajura-organic-red-apples",
                "Bajura High-Altitude Organic Red Apples",
                "बाजुराको अर्गानिक रातो स्याउ",
                cat_fruits, dist_bajura,
                "Crisp, sweet organic Royal Delicious apples grown in the cold Himalayan slopes of Bajura without chemical pesticides.",
                "बाजुराको हिमाली चिसो हावापानीमा प्राकृतिक रूपमा फलेका अत्यन्तै रसिला र स्वादिला राता स्याउहरू।",
                "Keshab Raj Joshi", "9858522333", "products/bajura_apples.jpg",
                "Autumn (Bhadra - Kartik)", "रु. १८० - २५०", "kg", True
            ),
            (
                "dadeldhura-wild-forest-timur",
                "Dadeldhura Wild Himalayan Timur",
                "डडेल्धुराको प्राकृतिक वन्य टिमुर",
                cat_spices, dist_dadeldhura,
                "Aromatic wild-harvested Sichuan pepper berries with a sharp citrus aroma, hand-picked in Dadeldhura oak forests.",
                "डडेल्धुराका पहाडी जंगलहरूबाट संकलित प्राकृतिक, सुगन्धित र जिब्रो झमझमाउने गुणस्तरीय टिमुर।",
                "Parbati Bohara", "9858633444", "products/dadeldhura_timur.jpg",
                "Autumn / Winter", "रु. १,२०० - १,५००", "kg", True
            ),
            (
                "darchula-cliff-wild-honey",
                "Darchula High-Himalayan Cliff Honey",
                "दार्चुलाको प्राकृतिक भीर मह",
                cat_spices, dist_darchula,
                "Pure raw wild medicinal honey harvested from giant Himalayan cliff bees nesting along deep river gorges.",
                "दार्चुलाका अग्ला भिरपहराहरूमा बस्ने भीर मौरीको मह, जसमा उच्च औषधीय र स्वास्थ्यवद्र्धक गुण हुन्छ।",
                "Dhan Singh Dhami", "9858744555", "products/darchula_honey.jpg",
                "Spring / Autumn", "रु. २,००० - २,५००", "kg", True
            ),
            (
                "baitadi-handwoven-wool-thulma",
                "Baitadi Traditional Handwoven Wool Thulma",
                "बैतडीको परम्परागत हातेबुना थुल्मा (राडी-पाखी)",
                cat_crafts, dist_baitadi,
                "Durable, warm woolen blanket hand-spun on wooden pedal-looms from pure local sheep fleece in Baitadi.",
                "बैतडीको रैथाने भेडाको ऊनबाट परम्परागत तानमा हातैले बुनिएको अत्यन्तै न्यानो र टिकाउ थुल्मा।",
                "Shanti Devi B.K.", "9858855666", "products/baitadi_thulma.jpg",
                "All Year (Best in Winter)", "रु. ४,५०० - ६,५००", "piece", True
            ),
        ]

        LocalProduct.objects.all().delete()
        for idx, (slug, n_en, n_ne, cat, dist, d_en, d_ne, farm, ph, img, sea, prc, un, feat) in enumerate(products_data):
            lp = LocalProduct.objects.create(
                slug=slug, name=n_en, name_en=n_en, name_ne=n_ne,
                category=cat, district=dist,
                description=d_en, description_en=d_en, description_ne=d_ne,
                farmer_name=farm, contact_phone=ph,
                image=img, image_url=f"/media/{img}",
                seasonality=sea, estimated_price_range=prc, unit=un,
                is_featured=feat, is_verified=True, status='approved'
            )
            created_producers[idx % len(created_producers)].products.add(lp)
        self.stdout.write(f"  products.LocalProduct: {LocalProduct.objects.count()} items")

    def seed_yatayat(self):
        from apps.yatayat.models import TransportService, TransportReport, EmergencyHelpline

        services_data = [
            (
                "Sudurpashchim Super Deluxe", "सुदूरपश्चिम सुपर डिलक्स",
                "AC Air Suspension Long Route", "वातानुकूलित लामो दूरी सेवा",
                "bus", "सुपर डिलक्स", "emerald",
                "Dhangadhi (धनगढी)", "Kathmandu (काठमाडौं)",
                ["Attariya", "Kohalpur", "Narayangarh"],
                "03:30 PM", "रु. २,१००", "38", "9858422111",
                "yatayat/bus_safal.jpg", "Includes AC, USB charging at each seat, mineral water, and dinner stopover."
            ),
            (
                "Mahakali Express Highway Bus", "महाकाली एक्सप्रेस डिलक्स",
                "Direct Western Trunk Route", "दैनिक द्रुत सेवा",
                "bus", "नियमित सेवा", "blue",
                "Mahendranagar (महेन्द्रनगर)", "Pokhara (पोखरा)",
                ["Dhangadhi", "Kohalpur", "Butwal"],
                "04:00 PM", "रु. १,९५०", "40", "9858433222",
                "yatayat/bus_dolphin.jpg", "Comfortable semi-sleeper reclining seats and luggage safety tags."
            ),
            (
                "Khaptad Hills 4WD Bolero", "खप्तड हिल्स बोलेरो जिप",
                "Mountain Offroad Shuttle", "पहाडी कच्ची सडक सेवा",
                "jeep", "पहाडी रुट", "brand",
                "Dipayal Silgadhi (दिपायल)", "Sanfebagar, Achham (साँफेबगर)",
                ["Chaukhute", "Bhatakatiya"],
                "07:30 AM", "रु. ६००", "8", "9858444333",
                "yatayat/jeep_bolero.jpg", "Heavy duty 4-wheel drive suited for hill roads and seasonal terrain."
            ),
            (
                "Dhangadhi-Dadeldhura Hiace Rapid", "धनगढी-डडेल्धुरा हाइस द्रुत सेवा",
                "Fast Passenger Commuter", "छिटो र छरितो यात्रा",
                "hiace", "द्रुत सेवा", "emerald",
                "Dhangadhi (धनगढी)", "Amargadhi, Dadeldhura (डडेल्धुरा)",
                ["Attariya", "Khanidanda", "Bhatkanda"],
                "Hourly from 06:00 AM", "रु. ६५०", "14", "9858455444",
                "yatayat/hiace_van.jpg", "Fast commuter mini-bus equipped with seatbelts and music system."
            ),
            (
                "Api Himal Border Transport", "अपि हिमाल सीमावर्ती यातायात",
                "Northern Frontier Express", "उत्तरी सीमावर्ती सेवा",
                "bus", "सिधा सेवा", "amber",
                "Attariya (अत्तरिया)", "Khalanga, Darchula (खलङ्गा)",
                ["Dadeldhura", "Patan", "Gokuleshwar"],
                "06:30 AM", "रु. १,४००", "32", "9858466555",
                "yatayat/bus_achham.jpg", "Experienced drivers specialized in winding Mahakali river valley highways."
            ),
        ]

        TransportService.objects.all().delete()
        created_services = []
        for t_en, t_ne, sub_en, sub_ne, stype, btext, bcol, orig, dest, stops, deptime, fare, seats, ph, img, nts in services_data:
            s = TransportService.objects.create(
                title=t_en, title_en=t_en, title_ne=t_ne,
                sub_title=sub_en, sub_title_en=sub_en, sub_title_ne=sub_ne,
                service_type=stype,
                badge_text=btext, badge_color=bcol,
                origin_name=orig, destination_name=dest,
                route_stops=stops,
                departure_time=deptime, estimated_fare=fare, total_seats=seats,
                contact_phone=ph, contact_numbers=[ph, "091-520100"],
                image=img, image_url=f"/media/{img}",
                notes=nts,
                status='approved', verified=True, is_active=True
            )
            created_services.append(s)
        self.stdout.write(f"  yatayat.TransportService: {TransportService.objects.count()} items")

        # Transport Reports
        reports_data = [
            (created_services[0], "inaccurate_info", "Departure was at 3:45 PM instead of 3:30 PM due to passenger check-in. Otherwise great bus.", "9848411222"),
            (created_services[1], "fare_issue", "Ticket counter charged exactly government approved fare. Very fair operator.", "9848522333"),
            (created_services[2], "road_condition", "Silgadhi to Sanfebagar road has minor gravel work near Bhatakatiya. Drive safe.", "9848633444"),
            (created_services[3], "positive_feedback", "Reached Dadeldhura in under 4 hours. Super fast and clean Hiace.", "9848744555"),
            (created_services[4], "schedule_update", "Morning departure moved to 7:00 AM during winter fog season.", "9848855666"),
        ]
        TransportReport.objects.all().delete()
        for srv, itype, desc, rph in reports_data:
            TransportReport.objects.create(service=srv, issue_type=itype, description=desc, reporter_phone=rph)
        self.stdout.write(f"  yatayat.TransportReport: {TransportReport.objects.count()} items")

        # Emergency Helpline (ensure at least 5)
        helplines_data = [
            ("Sudurpashchim Traffic Police Control", "traffic", "103", "24/7 Province Traffic Emergency Hotline", True, 1),
            ("Dhangadhi Central Bus Terminal Counter", "buspark", "091-521155", "Inquiry and ticket reservation desk", False, 2),
            ("Highway Police Patrol Unit (Attariya)", "police", "100", "Immediate Highway Security & Accidents", True, 3),
            ("Mahendranagar Transit Information Center", "helpdesk", "099-520200", "Western border crossing passenger helpdesk", False, 4),
            ("Dadeldhura Mountain Road Rescue Unit", "police", "096-420100", "Toll-free hill road clearance & towing help", True, 5),
        ]
        EmergencyHelpline.objects.all().delete()
        for tit, cat, ph, sub, is24, ordr in helplines_data:
            EmergencyHelpline.objects.create(
                title=tit, title_en=tit, title_ne=tit,
                category=cat, phone_number=ph, subtitle=sub,
                is_24_7=is24, order=ordr
            )
        self.stdout.write(f"  yatayat.EmergencyHelpline: {EmergencyHelpline.objects.count()} items")

    def seed_multimedia(self):
        from apps.multimedia.models import VideoItem, VideoComment, PhotoStory, PhotoStoryImage
        from apps.districts.models import District

        dist_kailali = District.objects.filter(slug='kailali').first()
        dist_doti = District.objects.filter(slug='doti').first()
        dist_kanchanpur = District.objects.filter(slug='kanchanpur').first()
        dist_darchula = District.objects.filter(slug='darchula').first()
        dist_achham = District.objects.filter(slug='achham').first()

        videos_data = [
            ("Journey Across Khaptad: 22 Meadows and Mystical Landscapes", "खप्तडको यात्रा: २२ पाटन र रहस्यमयी प्राकृतिक सौन्दर्य", "media/seed/videos/videos-001.jpg", "jNQXAC9IVRw", "12:45", 3420, 245, dist_doti),
            ("Karnali River Rafting Expedition and Wildlife Secrets", "कर्णाली नदीमा र्याफ्टिङ यात्रा र जलचरहरूको संसार", "media/seed/videos/videos-002.jpg", "7QUtEmk3Y4E", "08:30", 2180, 180, dist_kailali),
            ("Shuklaphanta Swamp Deer: Largest Herd in Asia", "शुक्लाफाँटाको फाँटमा बाह्रसिंगाको विशाल बथान", "media/seed/videos/videos-003.jpg", "ScMzIvxBSi4", "15:20", 4120, 310, dist_kanchanpur),
            ("Living Traditions of Far-West: Gaura and Deuda Dance", "सुदूरपश्चिमको मौलिक गौरा पर्व र देउडा भाका", "media/seed/videos/videos-004.jpg", "kJQP7kiw5Fk", "09:50", 5290, 420, dist_achham),
            ("Api Himal Trekking Guide: Untouched Wilderness of Darchula", "अपि हिमाल पदमार्ग: दार्चुलाको अद्वितीय हिमाली यात्रा", "media/seed/videos/videos-005.jpg", "fJ9rUzIMcZQ", "18:15", 3890, 275, dist_darchula),
        ]

        VideoItem.objects.all().delete()
        created_videos = []
        for t_en, t_ne, thm, yid, dur, vw, lk, dist in videos_data:
            v = VideoItem.objects.create(
                title=t_en, title_en=t_en, title_ne=t_ne,
                thumbnail=f"/{thm}",
                video_url=f"https://www.youtube.com/watch?v={yid}",
                youtube_id=yid,
                duration=dur, views=vw, likes=lk,
                publishedAt=timezone.now(),
                district=dist,
                isShort=False
            )
            created_videos.append(v)
        self.stdout.write(f"  multimedia.VideoItem: {VideoItem.objects.count()} items")

        # Video Comments
        vcomments = [
            ("Ramesh Joshi", "Dhangadhi", "Spectacular documentary. Khaptad is truly unmatched in South Asia."),
            ("Pramila Bhatt", "Kathmandu", "The deuda dance performance brought tears to my eyes. Beautiful culture!"),
            ("Chris Walker", "Sydney, Australia", "Adding Api Himal trek to my 2027 bucket list. Great camera work."),
            ("Kishor Chaudhary", "Mahendranagar", "The aerial footage of Shuklaphanta grasslands is stunning."),
            ("Gita Rawal", "Dipayal", "Proud to see Far-West nature documented in such high definition.")
        ]
        VideoComment.objects.all().delete()
        for idx, (aname, aloc, cont) in enumerate(vcomments):
            v = created_videos[idx % len(created_videos)]
            VideoComment.objects.create(video=v, authorName=aname, authorLocation=aloc, content=cont, likes=15)
        self.stdout.write(f"  multimedia.VideoComment: {VideoComment.objects.count()} items")

        # Photo Stories
        stories_data = [
            ("Wilderness of Shuklaphanta: Where Grasslands Touch the Sky", "शुक्लाफाँटाको विशाल घाँसे मैदान र वन्यजन्तु", "A photographic journey through the world's largest concentration of swamp deer.", "विश्वकै ठूलो बाह्रसिंगाको बथान पाइने शुक्लाफाँटाको मनमोहक तस्बिर कथा।", "photo_stories/story_tikapur.jpg", 18, "Prakash Bhatt", dist_kanchanpur),
            ("Colours of Deuda: Ancient Songs of Hill Valleys", "देउडाका रङहरू: पहाडी उपत्यकाको लोकजीवन", "Capturing traditional dancers in handmade local attire during annual village fairs.", "स्थानीय मेलापर्वमा परम्परागत पहिरन र देउडा खेलका जीवन्त झलकहरू।", "photo_stories/story_ugratara.jpg", 14, "Sarita Chaudhary", dist_achham),
            ("Ghodaghodi Ramsar Wetland: Birdwatcher's Paradise", "घोडाघोडी सिमसार: चराचुरुङ्गीहरूको क्रिडास्थल", "Documenting migratory Siberian ducks and marsh crocodiles across the 24 sacred lakes.", "घोडाघोडी ताल क्षेत्रमा पाइने दुर्लभ चरा र जलचरहरूको फोटो कथा।", "photo_stories/story_ghodaghodi.jpg", 22, "Jeevan Joshi", dist_kailali),
            ("High Alpine Springs of Surma Sarovar", "पवित्र सुरमा सरोवरको हिमाली यात्रा", "Trekking through blooming rhododendrons to the crystal alpine waters of Bajhang.", "बझाङको उच्च हिमाली भेगमा अवस्थित पवित्र सुरमा सरोवरको यात्रा वृत्तान्त।", "photo_stories/story_surma.jpg", 16, "Narendra Rawat", dist_doti),
            ("The Living Forts and Temples of Dadeldhura", "डडेल्धुराका ऐतिहासिक गढी र मन्दिरहरू", "Architectural study of Amargadhi battlements and sacred shrines.", "अमरगढी किल्ला र उग्रतारा मन्दिरको वास्तुकला र ऐतिहासिक गौरव।", "photo_stories/story_khaptad.jpg", 12, "Sunita Thapa", dist_darchula),
        ]

        PhotoStory.objects.all().delete()
        PhotoStoryImage.objects.all().delete()
        for idx, (t_en, t_ne, d_en, d_ne, cov, cnt, photog, dist) in enumerate(stories_data):
            ps = PhotoStory.objects.create(
                title=t_en, title_en=t_en, title_ne=t_ne,
                description=d_en, description_en=d_en, description_ne=d_ne,
                coverImage=f"/media/{cov}",
                imageCount=cnt,
                photographer=photog,
                publishedAt=timezone.now(),
                district=dist
            )
            PhotoStoryImage.objects.create(
                story=ps,
                image=cov,
                image_url=f"/media/{cov}",
                caption=t_en,
                caption_en=t_en,
                caption_ne=t_ne,
                order=1
            )
        self.stdout.write(f"  multimedia.PhotoStory: {PhotoStory.objects.count()} items")
        self.stdout.write(f"  multimedia.PhotoStoryImage: {PhotoStoryImage.objects.count()} items")

    def seed_ads(self):
        from apps.ads.models import BannerAd, PopupAd

        banner_ads = [
            ("Nepal Telecom 5G Far-West Rollout", "home", "top-leaderboard", "banner_ads/telecom_5g.jpg", "https://ntc.net.np", "Nepal Telecom 5G Banner", "Nepal Telecom", 10),
            ("Far-Western University Admissions 2026", "category", "billboard-mid", "banner_ads/university_leaderboard.jpg", "https://fwu.edu.np", "FWU Academic Admissions", "Far-Western University", 8),
            ("Rastriya Banijya Bank Agri-Loan Scheme", "article", "sidebar", "banner_ads/bank_sidebar.jpg", "https://rbb.com.np", "Agricultural Credit Support", "Rastriya Banijya Bank", 9),
            ("Explore Sudurpashchim Provincial Tourism Drive", "tourism", "billboard-mid", "banner_ads/tourism_billboard.jpg", "https://welcomenepal.com", "Tourism Promotion Campaign", "Sudur Tourism Board", 7),
            ("Yeti Airlines Dhangadhi Flight Connections", "all", "in-article", "banner_ads/roadblock_ad.jpg", "https://yetiairlines.com", "Fly directly to Dhangadhi", "Yeti Airlines", 6),
        ]

        BannerAd.objects.all().delete()
        for tit, pg, pl, img, tgt, alt, adv, prio in banner_ads:
            BannerAd.objects.create(
                title=tit, page=pg, placement=pl,
                image=img, image_url=f"/media/{img}",
                target_url=tgt, alt_text=alt, advertiser=adv,
                status='approved', is_active=True, priority=prio
            )
        self.stdout.write(f"  ads.BannerAd: {BannerAd.objects.count()} items")

        # Popup Ads (ensure 5)
        popup_ads = [
            ("Discover Khaptad Nature Retreat 2026", "banner_ads/tourism_billboard.jpg", "https://welcomenepal.com", "Sudur Tourism Board", 7),
            ("Nepal Telecom Unlimited 5G Data Pack", "banner_ads/telecom_5g.jpg", "https://ntc.net.np", "Nepal Telecom", 6),
            ("Bank Youth Entrepreneurship Loan 2026", "banner_ads/bank_sidebar.jpg", "https://rbb.com.np", "Rastriya Banijya Bank", 5),
            ("Far-Western University Master Degree Intake", "banner_ads/university_leaderboard.jpg", "https://fwu.edu.np", "Far-Western University", 8),
            ("Yeti Daily Direct Flights to Dhangadhi", "banner_ads/roadblock_ad.jpg", "https://yetiairlines.com", "Yeti Airlines", 6),
        ]
        PopupAd.objects.all().delete()
        for tit, img, tgt, adv, dur in popup_ads:
            PopupAd.objects.create(
                title=tit, title_en=tit, title_ne=tit,
                image=img, image_url=f"/media/{img}",
                target_url=tgt, advertiser=adv, duration_seconds=dur, is_active=True
            )
        self.stdout.write(f"  ads.PopupAd: {PopupAd.objects.count()} items")

    def seed_districts_partners_and_sliders(self):
        from apps.districts.models import District, Partner, DistrictSliderImage
        from django.core.management import call_command

        # Seed all 9 official district partners with their custom emblems
        call_command('seed_district_partners')

        districts = list(District.objects.all())

        # District Slider Images (ensure every key district has sliders)
        sliders = [
            (districts[0], "districts/slider/karnali_bridge.jpg", "Karnali Bridge gateway to Far-West"),
            (districts[1], "districts/slider/khaptad_national_park.jpg", "Khaptad National Park meadows"),
            (districts[2], "districts/slider/dodhara_chandani.jpg", "Dodhara Chandani Suspension Bridge"),
            (districts[3], "districts/slider/ugratara_temple.jpg", "Ugratara Bhagawati Temple Dadeldhura"),
            (districts[4], "districts/slider/api_himal.jpg", "Api Himal peak overlooking Darchula"),
        ]
        for dist, img, cap in sliders:
            DistrictSliderImage.objects.update_or_create(
                district=dist,
                image=img,
                defaults={
                    'caption': cap,
                    'caption_en': cap,
                    'caption_ne': cap,
                    'order': 1
                }
            )
        self.stdout.write(f"  districts.DistrictSliderImage: {DistrictSliderImage.objects.count()} items")

    def seed_video_interactions(self):
        from apps.multimedia.models import VideoItem, VideoComment, VideoLike, VideoCommentLike
        
        users = list(User.objects.filter(is_staff=True).order_by('id')[:5])
        videos = list(VideoItem.objects.all().order_by('id')[:5])
        comments = list(VideoComment.objects.all().order_by('id')[:5])

        if len(users) >= 5 and len(videos) >= 5:
            VideoLike.objects.all().delete()
            for idx in range(5):
                VideoLike.objects.create(video=videos[idx], user=users[idx])
            self.stdout.write(f"  multimedia.VideoLike: {VideoLike.objects.count()} items")

        if len(users) >= 5 and len(comments) >= 5:
            VideoCommentLike.objects.all().delete()
            for idx in range(5):
                VideoCommentLike.objects.create(comment=comments[idx], user=users[idx])
            self.stdout.write(f"  multimedia.VideoCommentLike: {VideoCommentLike.objects.count()} items")

    def seed_submissions(self):
        from apps.districts.models import District, PhotoSubmission, StorySubmission

        dist_doti = District.objects.filter(slug='doti').first()
        dist_kanchanpur = District.objects.filter(slug='kanchanpur').first()
        dist_kailali = District.objects.filter(slug='kailali').first()
        dist_darchula = District.objects.filter(slug='darchula').first()
        dist_dadeldhura = District.objects.filter(slug='dadeldhura').first()
        dist_baitadi = District.objects.filter(slug='baitadi').first()
        dist_achham = District.objects.filter(slug='achham').first()

        # 1. Photo Submissions (5 items)
        photo_submissions_data = [
            ("Kamal Thapa", dist_doti, "Autumn Mist Over Triveni Meadows", "Capturing morning mist rising over Triveni Dham at 3,100m in Khaptad National Park.", "contributions/photos/khaptad_mist.jpg", "approved"),
            ("Anita Chaudhary", dist_kanchanpur, "Herds of Swamp Deer at Golden Hour", "Sunset panorama of swamp deer grazing peacefully in the wetlands of Shuklaphanta.", "contributions/photos/shuklaphanta_herd.jpg", "approved"),
            ("Hemant Rawal", dist_kailali, "Chisapani Bridge Across Emerald Karnali", "Dramatic drone view of the single-tower cable stayed bridge over the raging Karnali river.", "contributions/photos/karnali_bridge_view.jpg", "approved"),
            ("Kalyan Joshi", dist_darchula, "Summit Glow on Mount Api (7,132m)", "First rays of sun striking the glaciated western face of Mt. Api from Byas valley basecamp.", "contributions/photos/api_glow.jpg", "approved"),
            ("Radha Bohara", dist_dadeldhura, "Historic Ramparts of Amargadhi Fort", "Ancient stonework, wooden bastions, and brass cannons preserved at Amargadhi fort in the morning mist.", "contributions/photos/amargadhi_fort_view.jpg", "approved"),
        ]
        PhotoSubmission.objects.all().delete()
        for photog, dist, tit, desc, img, stat in photo_submissions_data:
            PhotoSubmission.objects.create(
                photographer_name=photog,
                district=dist,
                title=tit,
                description=desc,
                image=img,
                status=stat
            )
        self.stdout.write(f"  districts.PhotoSubmission: {PhotoSubmission.objects.count()} items")

        # 2. Story Submissions (5 items)
        stories_data = [
            (
                "Tika Ram Joshi", dist_doti, "oral_history", "Khaptad Baba Hermitage",
                "The Living Legend of Khaptad Baba and Sacred Ayurvedic Wisdom",
                "In 1946, Swami Sachchidananda, later revered throughout South Asia as Khaptad Baba, arrived in these high alpine meadows. For over 50 years, he meditated in a simple wooden hermitage and authored seminal encyclopedias on spiritual science and Himalayan medicinal flora. Elders from Doti recall him healing villagers with rare herbs found only above 3,000 meters.",
                "approved"
            ),
            (
                "Sumitra Chaudhary", dist_kailali, "culture", "Tharu Craft & Living Traditions",
                "The Living Art of Tharu Astimki and Sacred Clay Murals",
                "Astimki is the sacred ritual of Tharu women during Krishna Janmashtami, where living rooms are transformed with hand-painted murals depicting nature, peacocks, elephants, and cosmological cycles using organic natural dyes made from rice flour and river clay.",
                "approved"
            ),
            (
                "Sher Bahadur Dhami", dist_darchula, "folklore", "Api Himal Folklore",
                "Legends of Api and Nampa: Guardian Deities of the Western Himalaya",
                "In Byas valley, oral tradition holds that Api and Nampa are divine sibling protectors who guard the passes between Nepal, India, and Tibet. Local shepherd communities sing devotional hymns before crossing high Himalayan pastures to ensure safe passage.",
                "approved"
            ),
            (
                "Nanda Kishor Bhatt", dist_baitadi, "history", "Katyuri Dynasties",
                "The Ancient Katyuri Dynasty Fortresses and Underground Naulas of Baitadi",
                "Before the modern unification of Nepal, Baitadi was governed by Katyuri kings who constructed subterranean stone water conduits (Naula) and monolithic stone temples in Patan and Jhulaghat, many of which remain intact after eight centuries.",
                "approved"
            ),
            (
                "Lila Devi Saud", dist_achham, "lifestyle", "Traditional Salt Caravan Trails",
                "Echoes of the Salt Caravan Trail: From Sanfebagar to Taklakot",
                "Before modern motorable roads, Achhami traders led goat and pony caravans laden with highland grain up to Tibetan border markets, returning with raw rock salt and sheep wool fleece. The journey took six arduous weeks across treacherous river gorges.",
                "approved"
            ),
        ]
        StorySubmission.objects.all().delete()
        for auth, dist, cat, sub_top, tit, desc, stat in stories_data:
            StorySubmission.objects.create(
                author_name=auth,
                district=dist,
                main_category=cat,
                sub_topic=sub_top,
                title=tit,
                description=desc,
                status=stat
            )
        self.stdout.write(f"  districts.StorySubmission: {StorySubmission.objects.count()} items")

    def seed_common(self):
        from apps.common.models import TrendingTopic, ContactInquiry, NewsletterSubscriber

        topics = [
            ("khaptad-tourism", "Khaptad Tourism", "खप्तड पर्यटन", 1450, 1),
            ("dodhara-port", "Dodhara Port", "दोधारा बन्दरगाह", 1280, 2),
            ("karnali-corridor", "Karnali Corridor", "कर्णाली करिडोर", 1120, 3),
            ("api-wildlife", "Api Wildlife", "अपि हिउँ चितुवा", 980, 4),
            ("local-products", "Local Products", "रैथाने उत्पादन", 890, 5),
        ]
        TrendingTopic.objects.all().delete()
        for slg, n_en, n_ne, sc, ordr in topics:
            TrendingTopic.objects.create(
                slug=slg, name=n_en, name_en=n_en, name_ne=n_ne,
                search_count=sc, order=ordr, is_active=True
            )
        self.stdout.write(f"  common.TrendingTopic: {TrendingTopic.objects.count()} items")

        inquiries = [
            ("Birendra Bahadur Singh", "birendra.singh@gmail.com", "9848412345", "Advertising on Sudur Chinari Header", "We are a local organic tea and herbs cooperative from Bajhang interested in running a billboard banner ad on your homepage for 3 months.", "advertising"),
            ("Dr. Pushpa Raj Joshi", "pushpa.joshi@fwu.edu.np", "9858423456", "Academic Symposium Media Partnership", "Far-Western University is organizing an international symposium on Himalayan climate and river ecology. We would like to partner with your editorial board.", "editorial"),
            ("Gita Saud", "gita.saud@kailali.org", "9848534567", "Heritage Archive Contribution", "Our youth cultural committee has documented 40 ancient Dotyali Deuda songs from Sanfebagar. How can we submit these for your cultural multimedia archive?", "general"),
            ("Rohan Shrestha", "rohan.trek@himalayanhikes.com", "9868645678", "Trek Trail Information Update", "The trekking route from Dipayal to Khaptad via Silgadhi has new wooden trail markers installed last week. Requesting an editorial note in the district travel guide.", "correction"),
            ("Nirmala Pant", "nirmala.homestay@gmail.com", "9858756789", "Listing Local Homestay in Stay Directory", "We operate a community-run homestay in Dodhara-Chandani near the suspension bridge and would like to be featured in your Hotel & Stay directory.", "editorial"),
        ]
        ContactInquiry.objects.all().delete()
        for nam, eml, ph, subj, msg, itype in inquiries:
            ContactInquiry.objects.create(name=nam, email=eml, phone=ph, subject=subj, message=msg, inquiry_type=itype)
        self.stdout.write(f"  common.ContactInquiry: {ContactInquiry.objects.count()} items")

        subscribers = [
            "sudur.reader@gmail.com",
            "farwest.investor@outlook.com",
            "kailali.journal@gmail.com",
            "himalayan.trekker@hotmail.com",
            "dhangadhi.commerce@org.np",
        ]
        NewsletterSubscriber.objects.all().delete()
        for eml in subscribers:
            NewsletterSubscriber.objects.create(email=eml, is_active=True)
        self.stdout.write(f"  common.NewsletterSubscriber: {NewsletterSubscriber.objects.count()} items")
