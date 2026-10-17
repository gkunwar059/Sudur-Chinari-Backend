from rest_framework import serializers
from apps.common.serializers_base import TranslatedAdminSerializerMixin, make_absolute_url
from .models import (
    District, DistrictTheme, DistrictStats, DistrictCulture,
    DistrictPlace, DistrictSliderImage, Partner
)

class DistrictThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistrictTheme
        fields = ['primary', 'dark', 'light', 'border', 'badgeBg', 'badgeText', 'gradient']


class DistrictStatsSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    palikas = serializers.SerializerMethodField()

    class Meta:
        model = DistrictStats
        fields = [
            'id', 'area', 'population', 'headquarters', 'elevation',
            'palikas', 'palikas_total', 'palikas_municipalities', 'palikas_rural',
            'majorRivers', 'literacy'
        ]

    def get_palikas(self, obj):
        return {
            'total': obj.palikas_total,
            'municipalities': obj.palikas_municipalities,
            'ruralMunicipalities': obj.palikas_rural,
        }


class DistrictCultureSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = DistrictCulture
        fields = ['id', 'folkDance', 'festivals', 'cuisine', 'dialects']


class DistrictPlaceSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = DistrictPlace
        fields = ['id', 'title', 'description', 'category', 'image', 'highlight']

    def get_image(self, obj):
        return make_absolute_url(obj.image, self.context.get('request'))


class DistrictSliderImageSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = DistrictSliderImage
        fields = ['id', 'image', 'caption', 'order']

    def get_image(self, obj):
        return make_absolute_url(obj.image, self.context.get('request'))


class DistrictSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    og_image = serializers.SerializerMethodField(read_only=True)
    theme = DistrictThemeSerializer(source='theme_data', read_only=True)
    stats = DistrictStatsSerializer(source='stats_data', read_only=True)
    culture = DistrictCultureSerializer(source='culture_data', read_only=True)
    places = DistrictPlaceSerializer(many=True, read_only=True)
    slider_images = DistrictSliderImageSerializer(many=True, read_only=True)
    storyCount = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = District
        fields = [
            'id', 'slug', 'name', 'description', 'history', 'meta_title', 'meta_description',
            'accentColor', 'heroImage', 'latitude', 'longitude', 'og_image',
            'theme', 'stats', 'culture', 'places', 'slider_images', 'storyCount',
        ]

    def get_og_image(self, obj):
        return make_absolute_url(obj.heroImage, self.context.get('request'))

    def get_storyCount(self, obj):
        if hasattr(obj, 'articles'):
            return obj.articles.count()
        return 0


class DistrictDetailSerializer(DistrictSerializer):
    pass


class PartnerSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    district_slug = serializers.CharField(source='district.slug', read_only=True, allow_null=True)
    district_name = serializers.CharField(source='district.name', read_only=True, allow_null=True)

    class Meta:
        model = Partner
        fields = ['id', 'name', 'role', 'image', 'url', 'district', 'district_slug', 'district_name']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.image:
            image_name = str(instance.image.name) if instance.image else ""
            if image_name and (instance.image.storage.exists(image_name) or image_name.startswith('partners/')):
                ret['image'] = make_absolute_url(instance.image, self.context.get('request'))
            else:
                ret['image'] = image_name
        return ret
