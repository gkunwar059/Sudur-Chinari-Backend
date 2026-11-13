from modeltranslation.translator import register, TranslationOptions
from .models import (
    District, DistrictStats, DistrictCulture, DistrictPlace,
    DistrictSliderImage, Partner
)

@register(District)
class DistrictTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'history', 'meta_title', 'meta_description')

@register(DistrictStats)
class DistrictStatsTranslationOptions(TranslationOptions):
    fields = ('headquarters', 'majorRivers')

@register(DistrictCulture)
class DistrictCultureTranslationOptions(TranslationOptions):
    fields = ('folkDance', 'festivals', 'cuisine', 'dialects')

@register(DistrictPlace)
class DistrictPlaceTranslationOptions(TranslationOptions):
    fields = (
        'title',
        'description',
        'highlight',
        'overview',
        'history',
        'location',
        'elevation',
        'area_or_size',
        'best_time_to_visit',
        'opening_hours',
        'entry_fee',
        'weather_summary',
        'how_to_reach',
        'festivals',
        'local_cuisine',
        'traditions',
        'languages',
        'travel_advisory',
    )

@register(DistrictSliderImage)
class DistrictSliderImageTranslationOptions(TranslationOptions):
    fields = ('caption',)

@register(Partner)
class PartnerTranslationOptions(TranslationOptions):
    fields = ('name', 'role')
