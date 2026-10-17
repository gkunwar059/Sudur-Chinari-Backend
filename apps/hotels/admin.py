from django.contrib import admin
from modeltranslation.admin import TranslationTabularInline
from apps.common.admin_base import BaseTranslatedAdmin
from .models import Amenity, Hotel, HotelRoom, HotelGallery, HotelNearbyPlace

@admin.register(Amenity)
class AmenityAdmin(BaseTranslatedAdmin):
    list_display = ('name_en', 'name_ne', 'icon', 'translation_complete')
    search_fields = ('name_en', 'name_ne')

class HotelRoomInline(TranslationTabularInline):
    model = HotelRoom
    extra = 1
    fields = ('name_en', 'name_ne', 'guests', 'bed_type_en', 'bed_type_ne', 'price', 'image')

class HotelGalleryInline(TranslationTabularInline):
    model = HotelGallery
    extra = 1
    fields = ('image', 'caption_en', 'caption_ne')

class HotelNearbyPlaceInline(TranslationTabularInline):
    model = HotelNearbyPlace
    extra = 1
    fields = ('name_en', 'name_ne', 'distance_en', 'distance_ne')

@admin.register(Hotel)
class HotelAdmin(BaseTranslatedAdmin):
    list_display = ('name_en', 'category', 'district', 'rating', 'translation_complete')
    list_filter = ('category', 'district', 'hotel_type')
    search_fields = ('name_en', 'name_ne', 'slug')
    prepopulated_fields = {'slug': ('name_en',)}
    filter_horizontal = ('amenities',)
    inlines = [HotelRoomInline, HotelGalleryInline, HotelNearbyPlaceInline]
    
    fieldsets = (
        ("Basic Setup", {
            "fields": (
                "name_en", "name_ne", "slug", "category", "district", "hotel_type",
                "hero_image"
            ),
        }),
        ("Location & Rating", {
            "fields": (
                "address_en", "address_ne", "municipality_en", "municipality_ne",
                "latitude", "longitude", "rating", "reviews_count"
            ),
        }),
        ("Details", {
            "fields": (
                "about_en", "about_ne", "story_en", "story_ne",
                "quote_text_en", "quote_text_ne", "quote_author",
                "highlights", "amenities"
            ),
        }),
        ("Contact & Reach", {
            "fields": (
                "phone1", "phone2", "email", "website", 
                "facebook_url", "instagram_url",
                "map_url", "reach_bus_en", "reach_bus_ne", 
                "reach_airport_en", "reach_airport_ne", 
                "reach_highway_en", "reach_highway_ne"
            ),
        }),
    )
