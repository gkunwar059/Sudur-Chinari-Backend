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
    fields = ('title', 'description')

@register(DistrictSliderImage)
class DistrictSliderImageTranslationOptions(TranslationOptions):
    fields = ('caption',)

@register(Partner)
class PartnerTranslationOptions(TranslationOptions):
    fields = ('name', 'role')
