from rest_framework import serializers
from apps.common.serializers_base import TranslatedAdminSerializerMixin, make_absolute_url
from .models import PopupAd, BannerAd

class PopupAdSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = PopupAd
        fields = ['id', 'title', 'image', 'target_url', 'advertiser', 'duration_seconds', 'is_active', 'created_at']

    def get_image(self, obj):
        if obj.image:
            return make_absolute_url(obj.image, self.context.get('request'))
        if obj.image_url:
            return make_absolute_url(obj.image_url, self.context.get('request'))
        return ""


class BannerAdSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    page_display = serializers.CharField(source='get_page_display', read_only=True)
    placement_display = serializers.CharField(source='get_placement_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    requested_by_username = serializers.SerializerMethodField()

    class Meta:
        model = BannerAd
        fields = [
            'id', 'title', 'page', 'page_display', 'custom_page_path',
            'placement', 'placement_display', 'image', 'image_url', 'target_url', 'alt_text',
            'advertiser', 'status', 'status_display', 'rejection_reason',
            'is_active', 'priority', 'requested_by', 'requested_by_username',
            'contact_name', 'contact_phone', 'contact_email', 'notes',
            'start_date', 'end_date', 'clicks_count', 'impressions_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'clicks_count', 'impressions_count', 'created_at', 'updated_at',
            'page_display', 'placement_display', 'status_display', 'requested_by_username'
        ]

    def get_image(self, obj):
        if obj.image:
            return make_absolute_url(obj.image, self.context.get('request'))
        if obj.image_url:
            return make_absolute_url(obj.image_url, self.context.get('request'))
        return ""

    def get_requested_by_username(self, obj):
        if obj.requested_by:
            return obj.requested_by.username or obj.requested_by.email
        return None


class BannerAdRequestSerializer(serializers.ModelSerializer):
    duration_days = serializers.IntegerField(required=False, default=30, write_only=True)
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = BannerAd
        fields = [
            'id', 'title', 'page', 'custom_page_path', 'placement',
            'image', 'image_url', 'target_url', 'alt_text', 'advertiser',
            'contact_name', 'contact_phone', 'contact_email', 'notes',
            'duration_days', 'start_date', 'end_date', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'created_at']

    def validate(self, attrs):
        if not attrs.get('image') and not attrs.get('image_url'):
            raise serializers.ValidationError({"image": "कृपया विज्ञापनको फोटो अपलोड गर्नुहोस् वा इमेज लिङ्क दिनुहोस् (Please upload an image or provide an image URL)."})
        return attrs

