from rest_framework import serializers
from apps.common.serializers_base import TranslatedAdminSerializerMixin, make_absolute_url
from .models import PopupAd

class PopupAdSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = PopupAd
        fields = ['id', 'title', 'image', 'target_url', 'advertiser', 'duration_seconds', 'is_active']

    def get_image(self, obj):
        if obj.image:
            return make_absolute_url(obj.image, self.context.get('request'))
        if obj.image_url:
            return make_absolute_url(obj.image_url, self.context.get('request'))
        return ""
