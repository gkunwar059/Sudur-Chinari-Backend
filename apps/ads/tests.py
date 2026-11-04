from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .models import BannerAd

User = get_user_model()

class BannerAdApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='advertiser_user',
            email='advertiser@example.com',
            password='Password123!'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin_staff',
            email='admin@example.com',
            password='AdminPassword123!'
        )

        # Seed an approved banner ad on home billboard-mid
        self.approved_ad = BannerAd.objects.create(
            title='Global Telecom Campaign',
            placement='billboard-mid',
            page='home',
            image_url='https://example.com/banner.jpg',
            target_url='https://ntc.net.np',
            advertiser='Nepal Telecom',
            status='approved',
            is_active=True,
            priority=10
        )

    def test_active_banner_ad_matching(self):
        # 1. Fetching for home & billboard-mid should return the ad
        resp = self.client.get('/api/v1/banner-ads/active/?placement=billboard-mid&page=home')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.data.get('active'))
        self.assertEqual(resp.data['data']['title'], 'Global Telecom Campaign')

        # 2. Fetching for a slot with no active ad should return active=False
        resp2 = self.client.get('/api/v1/banner-ads/active/?placement=sidebar&page=yatayat')
        self.assertEqual(resp2.status_code, 200)
        self.assertFalse(resp2.data.get('active'))
        self.assertIsNone(resp2.data.get('data'))

    def test_authenticated_user_can_request_ad(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            'title': 'New Kailali Organic Honey Campaign',
            'placement': 'sidebar',
            'page': 'products',
            'image_url': 'https://example.com/honey.jpg',
            'advertiser': 'Kailali Honey Producers',
            'contact_phone': '9848000000',
            'contact_email': 'honey@kailali.com',
            'notes': 'Please place on products page sidebar',
            'target_url': 'https://kailalihoney.com',
            'duration_days': 15
        }
        resp = self.client.post('/api/v1/banner-ads/request_ad/', payload)
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(resp.data.get('success'))

        ad = BannerAd.objects.get(title='New Kailali Organic Honey Campaign')
        # It must be pending and inactive until admin approves
        self.assertEqual(ad.status, 'pending')
        self.assertFalse(ad.is_active)
        self.assertEqual(ad.requested_by, self.user)
        self.assertEqual(ad.page, 'products')
        self.assertEqual(ad.placement, 'sidebar')

        # It must NOT show up as active on the products sidebar yet
        active_resp = self.client.get('/api/v1/banner-ads/active/?placement=sidebar&page=products')
        self.assertFalse(active_resp.data.get('active'))

        # Now admin approves it
        self.client.force_authenticate(user=self.admin_user)
        approve_resp = self.client.post(f'/api/v1/banner-ads/{ad.id}/approve/')
        self.assertEqual(approve_resp.status_code, 200)

        # Now it MUST show up as active on the products sidebar!
        active_resp_after = self.client.get('/api/v1/banner-ads/active/?placement=sidebar&page=products')
        self.assertTrue(active_resp_after.data.get('active'))
        self.assertEqual(active_resp_after.data['data']['id'], ad.id)

    def test_unauthenticated_request_is_blocked(self):
        resp = self.client.post('/api/v1/banner-ads/request_ad/', {'title': 'Spam Ad'})
        self.assertEqual(resp.status_code, 401)

    def test_click_and_impression_tracking(self):
        ad_id = self.approved_ad.id
        self.assertEqual(self.approved_ad.clicks_count, 0)
        self.assertEqual(self.approved_ad.impressions_count, 0)

        # Impression
        imp_resp = self.client.post(f'/api/v1/banner-ads/{ad_id}/impression/')
        self.assertEqual(imp_resp.status_code, 200)
        self.assertEqual(imp_resp.data['impressions'], 1)

        # Click
        click_resp = self.client.post(f'/api/v1/banner-ads/{ad_id}/click/')
        self.assertEqual(click_resp.status_code, 200)
        self.assertEqual(click_resp.data['clicks'], 1)
