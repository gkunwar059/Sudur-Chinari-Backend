import tempfile
from PIL import Image
from django.test import TestCase
from rest_framework.test import APIClient
from .models import District, DistrictPlace, PhotoSubmission, StorySubmission

class DistrictSubmissionsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.district = District.objects.create(name='Doti', slug='doti')

    def _generate_test_image(self):
        image = Image.new('RGB', (100, 100), color='blue')
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file, format='JPEG')
        tmp_file.seek(0)
        return tmp_file

    def test_photo_submission_with_multipart_querydict(self):
        img_file = self._generate_test_image()
        payload = {
            'contributor_name': 'Bikram Thapa',
            'district': 'doti',
            'title': 'Dipayal Silgadhi Sunrise',
            'content': 'Scenic view over the Seti River valley',
            'image': img_file
        }
        resp = self.client.post('/api/v1/photo-contributions/', payload, format='multipart')
        self.assertEqual(resp.status_code, 201)

        submission = PhotoSubmission.objects.get(title='Dipayal Silgadhi Sunrise')
        self.assertEqual(submission.photographer_name, 'Bikram Thapa')
        self.assertEqual(submission.description, 'Scenic view over the Seti River valley')
        self.assertEqual(submission.district, self.district)
        self.assertEqual(submission.status, 'pending')

    def test_story_submission_with_multipart_querydict(self):
        payload = {
            'author_name': 'Kamala Joshi',
            'district': 'doti',
            'main_category': 'tourism',
            'sub_topic': 'Historical Sites',
            'title': 'The Legends of Silgadhi Kot',
            'story': 'Ancient forts and tales from the Doti kingdom.',
        }
        resp = self.client.post('/api/v1/story-contributions/', payload, format='multipart')
        self.assertEqual(resp.status_code, 201)

        story = StorySubmission.objects.get(title='The Legends of Silgadhi Kot')
        self.assertEqual(story.author_name, 'Kamala Joshi')
        self.assertEqual(story.main_category, 'tourism')
        self.assertEqual(story.status, 'pending')


class DistrictPlaceSlugApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.district = District.objects.create(name='Kailali', slug='kailali')

    def test_place_auto_generates_unique_slug_and_exposes_in_api(self):
        p1 = DistrictPlace.objects.create(
            district=self.district,
            title='Ghodaghodi Lake Complex',
            title_en='Ghodaghodi Lake Complex',
            title_ne='घोडाघोडी ताल क्षेत्र',
            category='nature',
        )
        p2 = DistrictPlace.objects.create(
            district=self.district,
            title='Ghodaghodi Lake Complex',
            title_en='Ghodaghodi Lake Complex',
            title_ne='घोडाघोडी ताल क्षेत्र',
            category='nature',
        )
        self.assertEqual(p1.slug, 'ghodaghodi-lake-complex')
        self.assertEqual(p2.slug, 'ghodaghodi-lake-complex-1')

        district_resp = self.client.get('/api/v1/districts/kailali/?lang=ne')
        self.assertEqual(district_resp.status_code, 200)
        places = district_resp.data['places']
        self.assertEqual(len(places), 2)
        self.assertEqual(places[0]['slug'], 'ghodaghodi-lake-complex')
        self.assertEqual(places[1]['slug'], 'ghodaghodi-lake-complex-1')

        slug_resp = self.client.get('/api/v1/district-places/ghodaghodi-lake-complex/?lang=en')
        self.assertEqual(slug_resp.status_code, 200)
        self.assertEqual(slug_resp.data['slug'], 'ghodaghodi-lake-complex')

        id_resp = self.client.get(f'/api/v1/district-places/{p1.id}/')
        self.assertEqual(id_resp.status_code, 200)
        self.assertEqual(id_resp.data['slug'], 'ghodaghodi-lake-complex')

    def test_place_dynamic_detail_fields_serialize_by_language(self):
        place = DistrictPlace.objects.create(
            district=self.district,
            title='Tikapur Park',
            title_en='Tikapur Park',
            title_ne='टीकापुर पार्क',
            category='nature',
            highlight_en='Botanical Sanctuary',
            highlight_ne='उद्यान तथा विश्राम',
            overview_en='Lush riverside rose garden.',
            overview_ne='कर्णाली किनारको रमणीय उद्यान।',
            location_en='Tikapur-9, Kailali',
            location_ne='टीकापुर-९, कैलाली',
            best_time_to_visit_en='Nov – Mar',
            best_time_to_visit_ne='मंसिर – चैत',
            travel_advisory_en='Bring sunscreen and water.',
            travel_advisory_ne='पानी र घामबाट बच्ने सामग्री बोक्नुहोस्।',
        )
        resp_ne = self.client.get(f'/api/v1/district-places/{place.slug}/?lang=ne')
        self.assertEqual(resp_ne.status_code, 200)
        self.assertEqual(resp_ne.data['overview'], 'कर्णाली किनारको रमणीय उद्यान।')
        self.assertEqual(resp_ne.data['location'], 'टीकापुर-९, कैलाली')
        self.assertEqual(resp_ne.data['best_time_to_visit'], 'मंसिर – चैत')
        self.assertEqual(resp_ne.data['travel_advisory'], 'पानी र घामबाट बच्ने सामग्री बोक्नुहोस्।')

        resp_en = self.client.get(f'/api/v1/district-places/{place.slug}/?lang=en')
        self.assertEqual(resp_en.status_code, 200)
        self.assertEqual(resp_en.data['overview'], 'Lush riverside rose garden.')
        self.assertEqual(resp_en.data['highlight'], 'Botanical Sanctuary')

