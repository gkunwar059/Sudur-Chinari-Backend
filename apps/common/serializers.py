from rest_framework import serializers
from apps.common.serializers_base import TranslatedAdminSerializerMixin
from .models import TrendingTopic, ContactInquiry, NewsletterSubscriber

class TrendingTopicSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = TrendingTopic
        fields = ['id', 'name', 'slug', 'search_count', 'order', 'is_active']


class ContactInquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInquiry
        fields = ['id', 'name', 'email', 'phone', 'subject', 'message', 'inquiry_type', 'created_at']
        read_only_fields = ['created_at']


class NewsletterSubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscriber
        fields = ['id', 'email', 'is_active', 'created_at']
        read_only_fields = ['created_at']
