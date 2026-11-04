import tempfile
from PIL import Image
from django.test import TestCase
from rest_framework.test import APIClient
from .models import District, PhotoSubmission, StorySubmission

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
