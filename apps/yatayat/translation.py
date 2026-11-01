from modeltranslation.translator import register, TranslationOptions
from .models import TransportLocation, TransportService, EmergencyHelpline

@register(TransportLocation)
class TransportLocationTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(TransportService)
class TransportServiceTranslationOptions(TranslationOptions):
    fields = ('title', 'sub_title', 'badge_text', 'origin_name', 'destination_name', 'departure_time', 'estimated_fare', 'notes')

@register(EmergencyHelpline)
class EmergencyHelplineTranslationOptions(TranslationOptions):
    fields = ('title', 'subtitle')
