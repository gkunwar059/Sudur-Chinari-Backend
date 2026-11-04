from rest_framework import serializers
from apps.common.serializers_base import TranslatedAdminSerializerMixin, make_absolute_url
from .models import (
    District, DistrictTheme, DistrictStats, DistrictCulture,
    DistrictPlace, DistrictSliderImage, Partner,
    PhotoSubmission, StorySubmission
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


class DistrictSlugOrPkRelatedField(serializers.PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        if isinstance(data, str) and not data.isdigit():
            try:
                return self.get_queryset().get(slug=data)
            except self.get_queryset().model.DoesNotExist:
                self.fail('does_not_exist', pk_value=data)
        return super().to_internal_value(data)


class PhotoSubmissionSerializer(serializers.ModelSerializer):
    district = DistrictSlugOrPkRelatedField(queryset=District.objects.all())
    district_slug = serializers.CharField(source='district.slug', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = PhotoSubmission
        fields = [
            'id', 'photographer_name', 'district', 'district_slug', 'district_name',
            'title', 'description', 'image', 'status', 'created_at'
        ]
        read_only_fields = ['status', 'created_at']

    def to_internal_value(self, data):
        if hasattr(data, 'dict'):
            mapped = data.dict()
        elif hasattr(data, 'copy'):
            mapped = data.copy()
        else:
            mapped = dict(data)
        if 'contributor_name' in mapped and 'photographer_name' not in mapped:
            mapped['photographer_name'] = mapped['contributor_name']
        elif 'name' in mapped and 'photographer_name' not in mapped:
            mapped['photographer_name'] = mapped['name']
        if 'content' in mapped and 'description' not in mapped:
            mapped['description'] = mapped['content']
        return super().to_internal_value(mapped)


class StorySubmissionSerializer(serializers.ModelSerializer):
    district = DistrictSlugOrPkRelatedField(queryset=District.objects.all())
    district_slug = serializers.CharField(source='district.slug', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)

    media_file = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = StorySubmission
        fields = [
            'id', 'author_name', 'district', 'district_slug', 'district_name',
            'main_category', 'sub_topic', 'title', 'description', 'media_file',
            'status', 'created_at'
        ]
        read_only_fields = ['status', 'created_at']

    def to_internal_value(self, data):
        # Handle dict or QueryDict/multipart
        mapped = data.dict() if hasattr(data, 'dict') else dict(data)
        if 'image' in mapped and 'media_file' not in mapped:
            mapped['media_file'] = mapped['image']
        if 'contributor_name' in mapped and 'author_name' not in mapped:
            mapped['author_name'] = mapped['contributor_name']
        elif 'name' in mapped and 'author_name' not in mapped:
            mapped['author_name'] = mapped['name']
        if 'content' in mapped and 'description' not in mapped:
            mapped['description'] = mapped['content']
        elif 'story' in mapped and 'description' not in mapped:
            mapped['description'] = mapped['story']
        valid_cats = {c[0] for c in StorySubmission.CATEGORY_CHOICES}
        cat = (mapped.get('main_category') or '').lower().strip()
        if cat not in valid_cats:
            if 'life' in cat:
                cat = 'lifestyle'
            elif 'tour' in cat:
                cat = 'tourism'
            elif 'hist' in cat:
                cat = 'history'
            elif 'folk' in cat:
                cat = 'folklore'
            elif 'oral' in cat:
                cat = 'oral_history'
            elif 'mem' in cat:
                cat = 'memories'
            else:
                cat = 'culture'
        mapped['main_category'] = cat
        return super().to_internal_value(mapped)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.media_file:
            ret['media_file'] = make_absolute_url(instance.media_file, self.context.get('request'))
        return ret
