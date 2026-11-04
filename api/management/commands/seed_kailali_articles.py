from datetime import timedelta

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from api.models import Article, Author, Category, District, Tag

LOCALITIES = (
    ("Dhangadhi", "धनगढी"),
    ("Tikapur", "टीकापुर"),
    ("Ghodaghodi", "घोडाघोडी"),
    ("Lamkichuha", "लम्कीचुहा"),
    ("Bhajani", "भजनी"),
    ("Joshipur", "जोशीपुर"),
    ("Kailari", "कैलारी"),
    ("Mohanyal", "मोहन्याल"),
    ("Bardagoriya", "बर्दगोरिया"),
    ("Gauriganga", "गौरीगंगा"),
)

TOPICS = (
    {
        "category": "agriculture",
        "title_en": "Modern Agriculture Support Reaches Farmers",
        "title_ne": "आधुनिक कृषि सहयोग किसानसम्म पुग्यो",
        "topic_en": "agriculture support",
        "topic_ne": "कृषि सहयोग",
    },
    {
        "category": "education",
        "title_en": "Schools Receive New Learning Materials",
        "title_ne": "विद्यालयहरूले नयाँ सिकाइ सामग्री पाए",
        "topic_en": "school improvement",
        "topic_ne": "विद्यालय सुधार",
    },
    {
        "category": "health",
        "title_en": "Free Health Camp Serves Local Families",
        "title_ne": "निःशुल्क स्वास्थ्य शिविरले स्थानीय परिवारलाई सेवा दियो",
        "topic_en": "health outreach",
        "topic_ne": "स्वास्थ्य सेवा विस्तार",
    },
    {
        "category": "tourism",
        "title_en": "Tourism Promotion Drive Begins",
        "title_ne": "पर्यटन प्रवर्द्धन अभियान सुरु",
        "topic_en": "tourism promotion",
        "topic_ne": "पर्यटन प्रवर्द्धन",
    },
    {
        "category": "economy",
        "title_en": "Road Maintenance Work Accelerates",
        "title_ne": "सडक मर्मत कार्यले गति लियो",
        "topic_en": "road maintenance",
        "topic_ne": "सडक मर्मत",
    },
    {
        "category": "sports",
        "title_en": "Local Football Tournament Kicks Off",
        "title_ne": "स्थानीय फुटबल प्रतियोगिता सुरु",
        "topic_en": "sports development",
        "topic_ne": "खेलकुद विकास",
    },
    {
        "category": "culture",
        "title_en": "Cultural Heritage Preservation Initiative Launched",
        "title_ne": "सांस्कृतिक सम्पदा संरक्षण अभियान सुरु",
        "topic_en": "heritage preservation",
        "topic_ne": "सम्पदा संरक्षण",
    },
    {
        "category": "society",
        "title_en": "Community Forest Cleanup Campaign Held",
        "title_ne": "सामुदायिक वन सरसफाइ अभियान सम्पन्न",
        "topic_en": "forest conservation",
        "topic_ne": "वन संरक्षण",
    },
    {
        "category": "technology",
        "title_en": "Digital Service Center Opens for Citizens",
        "title_ne": "नागरिकका लागि डिजिटल सेवा केन्द्र सुरु",
        "topic_en": "digital service expansion",
        "topic_ne": "डिजिटल सेवा विस्तार",
    },
    {
        "category": "politics",
        "title_en": "Public Hearing Held on Local Development",
        "title_ne": "स्थानीय विकासमा सार्वजनिक सुनुवाइ सम्पन्न",
        "topic_en": "local governance reform",
        "topic_ne": "स्थानीय शासन सुधार",
    },
)

AUTHOR_SLUGS = (
    "ram-bahadur-thapa",
    "sita-devi-joshi",
    "bishnu-prasad-bohara",
    "kamala-bhandari",
    "kiran-shahi",
)


class Command(BaseCommand):
    help = "Create or update bilingual Kailali news stories for pagination testing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=100,
            help="Number of Kailali stories to create or update (default: 100).",
        )
        parser.add_argument(
            "--skip-images",
            action="store_true",
            help="Do not generate placeholder images after creating stories.",
        )

    def handle(self, *args, **options):
        count = options["count"]
        if count < 1:
            raise CommandError("--count must be a positive integer.")

        district = self.get_district()
        authors = self.get_authors()
        categories = self.get_categories()
        created_count = 0
        updated_count = 0

        with transaction.atomic():
            for index in range(count):
                locality_en, locality_ne = LOCALITIES[index % len(LOCALITIES)]
                topic = TOPICS[(index // len(LOCALITIES)) % len(TOPICS)]
                title_en = f"{locality_en}: {topic['title_en']}"
                title_ne = f"{locality_ne}मा {topic['title_ne']}"
                excerpt_en = (
                    f"Residents and officials in {locality_en}, Kailali, have "
                    f"started a new phase of {topic['topic_en']} focused on "
                    "better services, transparent implementation and long-term "
                    "community benefits."
                )
                excerpt_ne = (
                    f"कैलालीको {locality_ne}मा {topic['topic_ne']} सम्बन्धी नयाँ "
                    "चरण सुरु भएको छ, जसले राम्रो सेवा, पारदर्शी कार्यान्वयन र "
                    "दीर्घकालीन सामुदायिक लाभमा जोड दिने लक्ष्य राखेको छ।"
                )
                content_en = (
                    f"<p>{excerpt_en}</p>"
                    "<p>Local representatives said the effort was planned after "
                    "consultations with ward committees, community groups and "
                    "service providers. The next phase will focus on regular "
                    "monitoring, accountable spending and public feedback.</p>"
                    "<p>Residents can follow progress through ward notice boards "
                    "and the district information desk. Officials expect the "
                    "first results within three months.</p>"
                )
                content_ne = (
                    f"<p>{excerpt_ne}</p>"
                    "<p>स्थानीय प्रतिनिधिहरूका अनुसार वडा समिति, सामुदायिक "
                    "समूह र सेवा प्रदायकसँगको परामर्शपछि यो पहल तयार गरिएको "
                    "हो। आगामी चरणमा नियमित अनुगमन, जवाफदेही खर्च र "
                    "सार्वजनिक प्रतिक्रियामा ध्यान दिइनेछ।</p>"
                    "<p>नागरिकहरूले वडा सूचना पाटी र जिल्ला सूचना डेस्कमार्फत "
                    "प्रगतिको जानकारी लिन सक्नेछन्। अधिकारीहरूले तीन महिनाभित्र "
                    "पहिलो नतिजा देखिने अपेक्षा गरेका छन्।</p>"
                )

                article, created = Article.objects.update_or_create(
                    slug=f"kailali-stories-{index + 1:03d}",
                    defaults={
                        "title": title_en,
                        "title_en": title_en,
                        "title_ne": title_ne,
                        "excerpt": excerpt_en,
                        "excerpt_en": excerpt_en,
                        "excerpt_ne": excerpt_ne,
                        "content": content_en,
                        "content_en": content_en,
                        "content_ne": content_ne,
                        "imageCaption": f"{locality_en}, Kailali",
                        "imageCaption_en": f"{locality_en}, Kailali",
                        "imageCaption_ne": f"{locality_ne}, कैलाली",
                        "meta_title": title_en,
                        "meta_title_en": title_en,
                        "meta_title_ne": title_ne,
                        "meta_description": excerpt_en[:160],
                        "meta_description_en": excerpt_en[:160],
                        "meta_description_ne": excerpt_ne[:160],
                        "author": authors[index % len(authors)],
                        "category": categories[topic["category"]],
                        "district": district,
                        "status": "published",
                        "publishedAt": timezone.now() - timedelta(hours=index + 1),
                        "featured": index % 20 == 0,
                        "breaking": index == 0,
                        "popular": index % 5 == 0,
                        "readTime": 4 + index % 7,
                        "views": 100 + index * 17,
                        "likes": 5 + index * 3,
                    },
                )

                if not article.featuredImage or article.featuredImage.startswith(
                    "seed/articles/kailali-source-"
                ):
                    article.featuredImage = (
                        f"seed/articles/articles-{article.id:03d}.jpg"
                    )
                    article.save(update_fields=["featuredImage"])

                Tag.objects.filter(article=article).delete()
                for tag_name in (topic["title_en"], locality_en, "Kailali"):
                    Tag.objects.create(article=article, name=tag_name)

                if created:
                    created_count += 1
                else:
                    updated_count += 1

        total = Article.objects.filter(district=district).count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Kailali stories ready: {created_count} created, "
                f"{updated_count} updated, {total} total in Kailali."
            )
        )

        if not options["skip_images"]:
            call_command("seed_images")

    def get_district(self):
        district = District.objects.filter(slug="kailali").first()
        if district:
            return district

        return District.objects.create(
            slug="kailali",
            name="Kailali",
            name_en="Kailali",
            name_ne="कैलाली",
            description="Kailali district in Sudurpashchim Province.",
            description_en="Kailali district in Sudurpashchim Province.",
            description_ne="सुदूरपश्चिम प्रदेशको कैलाली जिल्ला।",
            accentColor="#05965B",
        )

    def get_authors(self):
        authors = list(Author.objects.filter(slug__in=AUTHOR_SLUGS))
        if authors:
            return authors

        authors = list(Author.objects.all()[:5])
        if authors:
            return authors

        author = Author.objects.create(
            slug="kailali-newsroom",
            name="Kailali Newsroom",
            name_en="Kailali Newsroom",
            name_ne="कैलाली न्यूजरुम",
            role="Staff Reporter",
            role_en="Staff Reporter",
            role_ne="कर्मचारी पत्रकार",
            bio="Kailali district reporting team.",
            bio_en="Kailali district reporting team.",
            bio_ne="कैलाली जिल्ला रिपोर्टिङ टोली।",
            district="Kailali",
        )
        return [author]

    def get_categories(self):
        fallback = (
            Category.objects.exclude(layout_type__in=["stay", "stayor_hotel"]).first()
            or Category.objects.create(
                slug="news",
                name="News",
                name_en="News",
                name_ne="समाचार",
                layout_type="news",
            )
        )
        categories = {}
        for slug in {topic["category"] for topic in TOPICS}:
            categories[slug] = (
                Category.objects.filter(slug=slug).first() or fallback
            )
        return categories
