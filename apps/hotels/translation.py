from modeltranslation.translator import register, TranslationOptions
from .models import Amenity, Hotel, HotelRoom, HotelGallery, HotelNearbyPlace

@register(Amenity)
class AmenityTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Hotel)
class HotelTranslationOptions(TranslationOptions):
    fields = ('name', 'hotel_type', 'address', 'municipality', 'short_description', 'about', 'story', 'quote_text', 'reach_bus', 'reach_airport', 'reach_highway')

@register(HotelRoom)
class HotelRoomTranslationOptions(TranslationOptions):
    fields = ('name', 'bed_type')

@register(HotelGallery)
class HotelGalleryTranslationOptions(TranslationOptions):
    fields = ('caption',)

@register(HotelNearbyPlace)
class HotelNearbyPlaceTranslationOptions(TranslationOptions):
    fields = ('name', 'distance')
