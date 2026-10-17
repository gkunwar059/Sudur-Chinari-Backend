from rest_framework import serializers
from apps.common.serializers_base import TranslatedAdminSerializerMixin, make_absolute_url
from apps.articles.serializers import CategorySerializer
from apps.districts.serializers import DistrictSerializer
from .models import Amenity, Hotel, HotelRoom, HotelGallery, HotelNearbyPlace

class AmenitySerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ['id', 'name', 'icon']


class HotelRoomSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    image = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = HotelRoom
        fields = ['id', 'name', 'guests', 'bed_type', 'image', 'price']
        
    def get_image(self, obj):
        return make_absolute_url(obj.image, self.context.get('request'))


class HotelGallerySerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    image = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = HotelGallery
        fields = ['id', 'image', 'caption']
        
    def get_image(self, obj):
        return make_absolute_url(obj.image, self.context.get('request'))


class HotelNearbyPlaceSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = HotelNearbyPlace
        fields = ['id', 'name', 'distance']


class HotelSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    district = DistrictSerializer(read_only=True)
    hero_image = serializers.SerializerMethodField(read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    rooms = HotelRoomSerializer(many=True, read_only=True)
    gallery = HotelGallerySerializer(many=True, read_only=True)
    nearby_places = HotelNearbyPlaceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Hotel
        fields = [
            'id', 'slug', 'name', 'hotel_type', 'category', 'district',
            'address', 'municipality', 'latitude', 'longitude', 'rating', 'reviews_count',
            'hero_image', 'short_description', 'about', 'story',
            'quote_text', 'quote_author',
            'phone1', 'phone2', 'email', 'website', 'facebook_url', 'instagram_url',
            'amenities', 'highlights',
            'map_url', 'reach_bus', 'reach_airport', 'reach_highway',
            'rooms', 'gallery', 'nearby_places'
        ]
        
    def get_hero_image(self, obj):
        return make_absolute_url(obj.hero_image, self.context.get('request'))
