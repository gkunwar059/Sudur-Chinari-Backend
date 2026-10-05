from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Category, Author, District, Article

class TranslationAPITestCase(APITestCase):
    def setUp(self):
        # Create users: staff and non-staff
        self.staff_user = User.objects.create_user(
            username='staff_test', password='password123', is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='regular_test', password='password123', is_staff=False
        )

        # Create Category
        self.category = Category.objects.create(
            slug='politics',
            name_en='Politics',
            name_ne='राजनीति',
            image=None
        )

        # Create Author
        self.author = Author.objects.create(
            slug='ram-sharma',
            name_en='Ram Sharma',
            name_ne='राम शर्मा',
            bio_en='Senior Journalist',
            bio_ne='वरिष्ठ पत्रकार',
            role='Journalist'
        )

        # Create District
        self.district = District.objects.create(
            slug='kailali',
            name_en='Kailali',
            name_ne='कैलाली',
            description_en='Kailali district description in English',
            description_ne='कैलाली जिल्लाको विवरण',
            heroImage='/images/districts/kailali.jpg'
        )

        # Create Article with complete Nepali translation
        self.article_with_ne = Article.objects.create(
            slug='karnali-bridge-opening',
            title_en='Karnali Bridge Opening',
            title_ne='कर्णाली पुल उद्घाटन',
            excerpt_en='Karnali bridge has opened for public.',
            excerpt_ne='कर्णाली पुल सर्वसाधारणका लागि खुला गरिएको छ।',
            content_en='Full English content of the article.',
            content_ne='नेपालीमा लेखको पूर्ण विवरण।',
            featuredImage='/images/karnali_bridge.jpg',
            status='published',
            author=self.author,
            category=self.category,
            district=self.district,
            publishedAt=timezone.now()
        )

        # Create Article WITHOUT Nepali translation (missing)
        self.article_no_ne = Article.objects.create(
            slug='tech-breakthrough-2026',
            title_en='Tech Breakthrough 2026',
            title_ne='',
            excerpt_en='English excerpt for tech news.',
            excerpt_ne='',
            content_en='English content only.',
            content_ne='',
            featuredImage='/images/tech.jpg',
            status='published',
            author=self.author,
            category=self.category,
            district=self.district,
            publishedAt=timezone.now()
        )

    def test_lang_en_returns_english(self):
        """?lang=en returns English content and Content-Language=en"""
        url = f'/api/v1/articles/{self.article_with_ne.slug}/?lang=en'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Karnali Bridge Opening')
        self.assertEqual(response.data['lang'], 'en')
        self.assertFalse(response.data['translation_missing'])
        self.assertEqual(response.headers.get('Content-Language'), 'en')
        # Public responses must never contain _en or _ne fields
        self.assertNotIn('title_en', response.data)
        self.assertNotIn('title_ne', response.data)

    def test_lang_ne_returns_nepali(self):
        """?lang=ne returns Nepali content and Content-Language=ne"""
        url = f'/api/v1/articles/{self.article_with_ne.slug}/?lang=ne'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'कर्णाली पुल उद्घाटन')
        self.assertEqual(response.data['lang'], 'ne')
        self.assertFalse(response.data['translation_missing'])
        self.assertEqual(response.headers.get('Content-Language'), 'ne')
        self.assertNotIn('title_en', response.data)
        self.assertNotIn('title_ne', response.data)

    def test_missing_nepali_value_falls_back_to_english_and_sets_translation_missing(self):
        """Missing Nepali value falls back to English and sets translation_missing=True"""
        url = f'/api/v1/articles/{self.article_no_ne.slug}/?lang=ne'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Content falls back to English
        self.assertEqual(response.data['title'], 'Tech Breakthrough 2026')
        # lang served is English
        self.assertEqual(response.data['lang'], 'en')
        # translation_missing is True
        self.assertTrue(response.data['translation_missing'])
        self.assertEqual(response.headers.get('Content-Language'), 'en')

    def test_missing_or_invalid_lang_defaults_to_english(self):
        """Missing or invalid ?lang= parameter defaults to English"""
        # Missing lang
        url = f'/api/v1/articles/{self.article_with_ne.slug}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Karnali Bridge Opening')
        self.assertEqual(response.data['lang'], 'en')
        self.assertEqual(response.headers.get('Content-Language'), 'en')

        # Invalid lang
        url_invalid = f'/api/v1/articles/{self.article_with_ne.slug}/?lang=fr'
        response_invalid = self.client.get(url_invalid)
        self.assertEqual(response_invalid.status_code, status.HTTP_200_OK)
        self.assertEqual(response_invalid.data['title'], 'Karnali Bridge Opening')
        self.assertEqual(response_invalid.data['lang'], 'en')
        self.assertEqual(response_invalid.headers.get('Content-Language'), 'en')

    def test_lang_all_as_staff_returns_en_and_ne_fields(self):
        """?lang=all as staff returns _en and _ne fields for translatable fields"""
        self.client.force_authenticate(user=self.staff_user)
        url = f'/api/v1/articles/{self.article_with_ne.slug}/?lang=all'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('title_en', response.data)
        self.assertIn('title_ne', response.data)
        self.assertEqual(response.data['title_en'], 'Karnali Bridge Opening')
        self.assertEqual(response.data['title_ne'], 'कर्णाली पुल उद्घाटन')
        self.assertIn('excerpt_en', response.data)
        self.assertIn('excerpt_ne', response.data)

    def test_lang_all_as_anonymous_or_non_staff_returns_single_language_shape(self):
        """?lang=all as anonymous or non-staff ignores 'all' and returns single-language shape without leaking both languages"""
        url = f'/api/v1/articles/{self.article_with_ne.slug}/?lang=all'

        # Anonymous user
        response_anon = self.client.get(url)
        self.assertEqual(response_anon.status_code, status.HTTP_200_OK)
        self.assertNotIn('title_en', response_anon.data)
        self.assertNotIn('title_ne', response_anon.data)
        self.assertEqual(response_anon.data['title'], 'Karnali Bridge Opening')

        # Regular non-staff user
        self.client.force_authenticate(user=self.regular_user)
        response_user = self.client.get(url)
        self.assertEqual(response_user.status_code, status.HTTP_200_OK)
        self.assertNotIn('title_en', response_user.data)
        self.assertNotIn('title_ne', response_user.data)
        self.assertEqual(response_user.data['title'], 'Karnali Bridge Opening')

    def test_accept_language_header_is_ignored(self):
        """Accept-Language header does NOT change the response language; query param alone decides"""
        # Header asks for ne, but no ?lang= query param
        url = f'/api/v1/articles/{self.article_with_ne.slug}/'
        response = self.client.get(url, HTTP_ACCEPT_LANGUAGE='ne')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Karnali Bridge Opening')
        self.assertEqual(response.headers.get('Content-Language'), 'en')

        # Header asks for ne, query param is en
        url_en = f'/api/v1/articles/{self.article_with_ne.slug}/?lang=en'
        response_en = self.client.get(url_en, HTTP_ACCEPT_LANGUAGE='ne')
        self.assertEqual(response_en.status_code, status.HTTP_200_OK)
        self.assertEqual(response_en.data['title'], 'Karnali Bridge Opening')
        self.assertEqual(response_en.headers.get('Content-Language'), 'en')

    def test_sitemap_endpoint_returns_correct_has_ne_and_updated_at(self):
        """Sitemap endpoint returns list with type, slug, updated_at (ISO 8601), and has_ne boolean"""
        # Check both /api/sitemap/ and /api/v1/sitemap/
        for sitemap_url in ('/api/sitemap/', '/api/v1/sitemap/'):
            response = self.client.get(sitemap_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIsInstance(response.data, list)

            # Map by slug
            by_slug = {item['slug']: item for item in response.data}

            # Check article with ne
            self.assertIn(self.article_with_ne.slug, by_slug)
            art_ne = by_slug[self.article_with_ne.slug]
            self.assertEqual(art_ne['type'], 'article')
            self.assertTrue(art_ne['has_ne'])
            self.assertIn('T', art_ne['updated_at'])

            # Check article without ne
            self.assertIn(self.article_no_ne.slug, by_slug)
            art_no = by_slug[self.article_no_ne.slug]
            self.assertEqual(art_no['type'], 'article')
            self.assertFalse(art_no['has_ne'])
            self.assertIn('T', art_no['updated_at'])

            # Check category
            self.assertIn(self.category.slug, by_slug)
            cat_entry = by_slug[self.category.slug]
            self.assertEqual(cat_entry['type'], 'category')
            self.assertTrue(cat_entry['has_ne'])

            # Check district
            self.assertIn(self.district.slug, by_slug)
            dist_entry = by_slug[self.district.slug]
            self.assertEqual(dist_entry['type'], 'district')
            self.assertTrue(dist_entry['has_ne'])

    def test_staff_write_endpoints_accept_en_and_ne_fields(self):
        """Write endpoints (create/update) for staff accept _en and _ne fields"""
        self.client.force_authenticate(user=self.staff_user)
        payload = {
            'slug': 'science',
            'name_en': 'Science',
            'name_ne': 'विज्ञान',
        }
        create_resp = self.client.post('/api/v1/categories/', payload, format='json')
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)

        # Retrieve with ?lang=en
        resp_en = self.client.get('/api/v1/categories/science/?lang=en')
        self.assertEqual(resp_en.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_en.data['name'], 'Science')

        # Retrieve with ?lang=ne
        resp_ne = self.client.get('/api/v1/categories/science/?lang=ne')
        self.assertEqual(resp_ne.status_code, status.HTTP_200_OK)
        self.assertEqual(resp_ne.data['name'], 'विज्ञान')

    def test_detail_seo_fields_and_absolute_urls(self):
        """Detail responses include meta_title, meta_description, and absolute og_image"""
        url = f'/api/v1/articles/{self.article_with_ne.slug}/?lang=en'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('meta_title', response.data)
        self.assertIn('meta_description', response.data)
        self.assertIn('og_image', response.data)
        self.assertTrue(response.data['og_image'].startswith('http://') or response.data['og_image'].startswith('https://'))
        self.assertTrue(response.data['featuredImage'].startswith('http://') or response.data['featuredImage'].startswith('https://'))


class UserAuthPhoneTestCase(APITestCase):
    def test_registration_with_phone_auto_generates_username(self):
        """User registration with phone auto-generates username"""
        payload = {
            'phone': '9841234567',
            'password': 'StrongPassword#2026',
            'first_name': 'Ramesh Saud',
            'email': 'ramesh@example.com'
        }
        res = self.client.post('/api/v1/auth/users/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED, res.data)
        self.assertEqual(res.data['username'], 'user_9841234567')
        self.assertEqual(res.data['phone'], '9841234567')

        # Check DB user & profile
        user = User.objects.get(username='user_9841234567')
        self.assertEqual(user.profile.phone, '9841234567')
        self.assertEqual(user.first_name, 'Ramesh Saud')

    def test_registration_without_phone_fails(self):
        """Phone number is required during user registration"""
        payload = {
            'password': 'StrongPassword#2026',
            'first_name': 'No Phone User'
        }
        res = self.client.post('/api/v1/auth/users/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', res.data)

    def test_duplicate_phone_fails(self):
        """Duplicate phone number is rejected"""
        payload1 = {
            'phone': '9840001111',
            'password': 'StrongPassword#2026',
        }
        res1 = self.client.post('/api/v1/auth/users/', payload1, format='json')
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)

        payload2 = {
            'phone': '9840001111',
            'password': 'AnotherPassword#2026',
        }
        res2 = self.client.post('/api/v1/auth/users/', payload2, format='json')
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', res2.data)

    def test_jwt_login_with_phone_number(self):
        """User can authenticate / log in with phone number"""
        # Register user first
        self.client.post('/api/v1/auth/users/', {
            'phone': '9849998888',
            'password': 'StrongPassword#2026',
        }, format='json')

        # Login with phone as username
        login_res = self.client.post('/api/v1/auth/jwt/create/', {
            'username': '9849998888',
            'password': 'StrongPassword#2026',
        }, format='json')
        self.assertEqual(login_res.status_code, status.HTTP_200_OK, login_res.data)
        self.assertIn('access', login_res.data)
        self.assertIn('refresh', login_res.data)

        # Login with hyphenated phone works as well
        login_res2 = self.client.post('/api/v1/auth/jwt/create/', {
            'username': '984-999-8888',
            'password': 'StrongPassword#2026',
        }, format='json')
        self.assertEqual(login_res2.status_code, status.HTTP_200_OK, login_res2.data)
