import tempfile
from PIL import Image
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.districts.models import District
from .models import ProductCategory, LocalProduct

User = get_user_model()

class LocalProductApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.district, _ = District.objects.get_or_create(slug='baitadi', defaults={'name': 'Baitadi'})
        self.category, _ = ProductCategory.objects.get_or_create(slug='fruits', defaults={'name': 'Fruits'})
        self.staff_user = User.objects.create_superuser(
            username='staff_admin',
            email='staff@example.com',
            password='AdminPassword123!'
        )

    def _generate_test_image(self):
        image = Image.new('RGB', (100, 100), color='green')
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file, format='JPEG')
        tmp_file.seek(0)
        return tmp_file

    def test_multipart_product_submission_handles_querydict(self):
        img_file = self._generate_test_image()
        payload = {
            'product_name': 'Baitadi Hill Oranges',
            'category_slug': 'fruits',
            'district': str(self.district.id),
            'farmer_name': 'Ram Bahadur',
            'contact_phone': '9848111111',
            'description': 'Fresh organic oranges from Baitadi hills',
            'seasonality': 'Winter',
            'estimated_price_range': 'Rs. 120 / kg',
            'unit': 'kg',
            'image': img_file,
        }
        resp = self.client.post('/api/v1/products/', payload, format='multipart')
        self.assertEqual(resp.status_code, 201)

        product = LocalProduct.objects.get(name='Baitadi Hill Oranges')
        self.assertEqual(product.slug, 'baitadi-hill-oranges')
        self.assertEqual(product.category, self.category)
        self.assertEqual(product.district, self.district)
        # Public submission must be pending & unverified
        self.assertEqual(product.status, 'pending')
        self.assertFalse(product.is_verified)

    def test_public_queryset_only_shows_approved_products(self):
        LocalProduct.objects.create(
            name='Approved Honey',
            slug='approved-honey',
            category=self.category,
            district=self.district,
            status='approved'
        )
        LocalProduct.objects.create(
            name='Pending Honey',
            slug='pending-honey',
            category=self.category,
            district=self.district,
            status='pending'
        )

        resp = self.client.get('/api/v1/products/')
        self.assertEqual(resp.status_code, 200)
        names = [item['name'] for item in resp.data.get('results', resp.data)]
        self.assertIn('Approved Honey', names)
        self.assertNotIn('Pending Honey', names)
