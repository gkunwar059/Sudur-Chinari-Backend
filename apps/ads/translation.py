from modeltranslation.translator import register, TranslationOptions
from .models import PopupAd

@register(PopupAd)
class PopupAdTranslationOptions(TranslationOptions):
    fields = ('title',)
