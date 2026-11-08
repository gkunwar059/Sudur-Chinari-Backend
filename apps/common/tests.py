from django.test import TestCase
from rest_framework.test import APIClient
from apps.common.models import TrendingTopic, ContactInquiry, NewsletterSubscriber
from apps.articles.models import Article, Category, Author
from apps.districts.models import District
from apps.products.models import LocalProduct, ProductCategory
from apps.yatayat.models import TransportService

class GlobalSearchAndCommonApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.district, _ = District.objects.get_or_create(slug='kailali', defaults={'name': 'Kailali'})
        self.category, _ = Category.objects.get_or_create(slug='economy', defaults={'name': 'Economy'})
        self.author, _ = Author.objects.get_or_create(name='Reporter 1')

        # Published article vs Draft article
        self.published_article = Article.objects.create(
            title_en='Kailali Agriculture Growth',
            excerpt_en='Remarkable growth in Kailali farming.',
            slug='kailali-agri-growth',
            category=self.category,
            district=self.district,
            author=self.author,
            status='published'
        )
        self.draft_article = Article.objects.create(
            title_en='Kailali Secret Draft Story',
            excerpt_en='Confidential draft about Kailali.',
            slug='kailali-secret-draft',
            category=self.category,
            district=self.district,
            author=self.author,
            status='draft'
        )

        # Approved product vs Pending product
        self.prod_cat = ProductCategory.objects.create(name='Agro', slug='agro')
        self.approved_product = LocalProduct.objects.create(
            name='Kailali Organic Honey',
            slug='kailali-organic-honey',
            category=self.prod_cat,
            district=self.district,
            status='approved'
        )
        self.pending_product = LocalProduct.objects.create(
            name='Kailali Unapproved Apples',
            slug='kailali-unapproved-apples',
            category=self.prod_cat,
            district=self.district,
            status='pending'
        )

        # Approved & active Yatayat vs Inactive/Pending Yatayat
        self.active_yatayat = TransportService.objects.create(
            title='Kailali Express Deluxe',
            origin_name='Dhangadhi',
            destination_name='Kathmandu',
            status='approved',
            is_active=True
        )
        self.inactive_yatayat = TransportService.objects.create(
            title='Kailali Inactive Bus',
            origin_name='Dhangadhi',
            destination_name='Pokhara',
            status='pending',
            is_active=False
        )

        # Trending topic
        self.trending = TrendingTopic.objects.create(
            name_en='Kailali',
            slug='kailali',
            search_count=5
        )

    def test_global_search_filters_published_and_approved_only(self):
        resp = self.client.get('/api/v1/search/?q=Kailali')
        self.assertEqual(resp.status_code, 200)
        data = resp.data

        # 1. Articles check
        article_titles = [a['title'] for a in data['articles']]
        self.assertIn('Kailali Agriculture Growth', article_titles)
        self.assertNotIn('Kailali Secret Draft Story', article_titles)

        # 2. Products check
        product_names = [p['name'] for p in data['products']]
        self.assertIn('Kailali Organic Honey', product_names)
        self.assertNotIn('Kailali Unapproved Apples', product_names)

        # 3. Yatayat check
        yatayat_titles = [y['title'] for y in data['yatayat']]
        self.assertIn('Kailali Express Deluxe', yatayat_titles)
        self.assertNotIn('Kailali Inactive Bus', yatayat_titles)

        # 4. Atomic search count increment check
        self.trending.refresh_from_db()
        self.assertEqual(self.trending.search_count, 6)

    def test_newsletter_subscription(self):
        resp = self.client.post('/api/v1/newsletter/', {'email': 'subscriber@example.com'})
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(NewsletterSubscriber.objects.filter(email='subscriber@example.com').exists())

        # Subscribing again should return 200 OK without duplicating
        resp2 = self.client.post('/api/v1/newsletter/', {'email': 'subscriber@example.com'})
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(NewsletterSubscriber.objects.filter(email='subscriber@example.com').count(), 1)

    def test_contact_inquiry_submission(self):
        payload = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'General Inquiry',
            'message': 'Hello from Sudurpashchim digital.',
            'inquiry_type': 'general'
        }
        resp = self.client.post('/api/v1/contact-inquiries/', payload)
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(ContactInquiry.objects.filter(email='john@example.com').exists())
