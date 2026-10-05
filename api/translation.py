from modeltranslation.translator import register, TranslationOptions
from .models import (
    Category,
    Author,
    District,
    Article,
    VideoItem,
    PhotoStory,
    BreakingNews,
    Partner,
    DistrictStats,
    DistrictCulture,
    DistrictPlace,
    DistrictSliderImage,
    Amenity,
    Hotel,
    HotelRoom,
    HotelGallery,
    HotelNearbyPlace,
)

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Author)
class AuthorTranslationOptions(TranslationOptions):
    fields = ('name', 'bio')

@register(District)
class DistrictTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'meta_title', 'meta_description')

@register(Article)
class ArticleTranslationOptions(TranslationOptions):
    fields = ('title', 'excerpt', 'content', 'imageCaption', 'meta_title', 'meta_description')

@register(VideoItem)
class VideoItemTranslationOptions(TranslationOptions):
    fields = ('title',)

@register(PhotoStory)
class PhotoStoryTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

@register(BreakingNews)
class BreakingNewsTranslationOptions(TranslationOptions):
    fields = ('text',)

@register(Partner)
class PartnerTranslationOptions(TranslationOptions):
    fields = ('name', 'role')

@register(DistrictStats)
class DistrictStatsTranslationOptions(TranslationOptions):
    fields = ('headquarters', 'majorRivers')

@register(DistrictCulture)
class DistrictCultureTranslationOptions(TranslationOptions):
    fields = ('folkDance', 'festivals', 'cuisine', 'dialects')

@register(DistrictPlace)
class DistrictPlaceTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

@register(DistrictSliderImage)
class DistrictSliderImageTranslationOptions(TranslationOptions):
    fields = ('caption',)

@register(Amenity)
class AmenityTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Hotel)
class HotelTranslationOptions(TranslationOptions):
    fields = ('name', 'hotel_type', 'address', 'municipality', 'about', 'story', 'reach_bus', 'reach_airport', 'reach_highway')

@register(HotelRoom)
class HotelRoomTranslationOptions(TranslationOptions):
    fields = ('name', 'bed_type')

@register(HotelGallery)
class HotelGalleryTranslationOptions(TranslationOptions):
    fields = ('caption',)

@register(HotelNearbyPlace)
class HotelNearbyPlaceTranslationOptions(TranslationOptions):
    fields = ('name', 'distance')

