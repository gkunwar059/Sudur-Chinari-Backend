from rest_framework import serializers
from apps.common.serializers_base import TranslatedAdminSerializerMixin
from apps.districts.serializers import DistrictSerializer
from .models import VideoItem, PhotoStory

class VideoItemSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    district = DistrictSerializer(read_only=True)

    class Meta:
        model = VideoItem
        fields = ['id', 'title', 'thumbnail', 'duration', 'views', 'publishedAt', 'district', 'isShort']


class PhotoStorySerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    district = DistrictSerializer(read_only=True)

    class Meta:
        model = PhotoStory
        fields = ['id', 'title', 'description', 'coverImage', 'imageCount', 'photographer', 'publishedAt', 'district']
