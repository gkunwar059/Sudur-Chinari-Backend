from modeltranslation.translator import register, TranslationOptions
from .models import TrendingTopic

@register(TrendingTopic)
class TrendingTopicTranslationOptions(TranslationOptions):
    fields = ('name',)
