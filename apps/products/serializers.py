from django.utils.text import slugify
from rest_framework import serializers
from apps.common.serializers_base import TranslatedAdminSerializerMixin, make_absolute_url
from apps.districts.serializers import DistrictSerializer, DistrictSlugOrPkRelatedField
from apps.districts.models import District
from .models import ProductCategory, LocalProduct, ProductProducer

class ProductCategorySerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'slug', 'icon', 'order', 'is_active']


class ProductProducerSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    district_name = serializers.CharField(source='district.name', read_only=True)
    district_slug = serializers.CharField(source='district.slug', read_only=True)
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = ProductProducer
        fields = [
            'id', 'name', 'district', 'district_name', 'district_slug',
            'municipality_address', 'phone', 'experience_years',
            'avatar', 'bio', 'is_verified', 'created_at'
        ]

    def get_avatar(self, obj):
        if obj.avatar:
            return make_absolute_url(obj.avatar, self.context.get('request'))
        return obj.avatar_url or None


class LocalProductSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    district = DistrictSlugOrPkRelatedField(queryset=District.objects.all(), required=False, allow_null=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    district_slug = serializers.CharField(source='district.slug', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    image = serializers.SerializerMethodField()
    producers = ProductProducerSerializer(many=True, read_only=True)
    producer_count = serializers.SerializerMethodField()
    slug = serializers.SlugField(required=False, allow_blank=True)

    class Meta:
        model = LocalProduct
        fields = [
            'id', 'name', 'slug', 'category', 'category_slug', 'category_name',
            'district', 'district_slug', 'district_name', 'description',
            'farmer_name', 'contact_phone',
            'image', 'seasonality', 'estimated_price_range', 'unit',
            'is_featured', 'is_verified', 'status', 'producers', 'producer_count', 'created_at'
        ]
        read_only_fields = ['status', 'is_verified', 'created_at']

    def get_image(self, obj):
        if obj.image:
            return make_absolute_url(obj.image, self.context.get('request'))
        return obj.image_url or None

    def get_producer_count(self, obj):
        return obj.producers.count()

    def to_internal_value(self, data):
        if hasattr(data, 'dict'):
            mapped = data.dict()
        elif hasattr(data, 'copy'):
            mapped = data.copy()
        else:
            mapped = dict(data)

        # Allow 'product_name' alias for 'name'
        if 'product_name' in mapped and 'name' not in mapped:
            mapped['name'] = mapped['product_name']

        # Allow 'category_slug' alias to resolve category ForeignKey
        if 'category_slug' in mapped and 'category' not in mapped:
            cat = ProductCategory.objects.filter(slug__iexact=mapped['category_slug']).first()
            if cat:
                mapped['category'] = cat.id
            else:
                first_cat = ProductCategory.objects.first()
                if first_cat:
                    mapped['category'] = first_cat.id

        # Generate slug if missing
        if not mapped.get('slug'):
            base = slugify(mapped.get('name', 'product')) or 'product'
            counter = 1
            unique_slug = base
            while LocalProduct.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base}-{counter}"
                counter += 1
            mapped['slug'] = unique_slug

        return super().to_internal_value(mapped)

    def create(self, validated_data):
        # Handle file upload for 'image' field if passed in initial_data or context
        request = self.context.get('request')
        if request and request.FILES and 'image' in request.FILES:
            validated_data['image'] = request.FILES['image']
        return super().create(validated_data)
