from modeltranslation.translator import register, TranslationOptions
from .models import VideoItem, PhotoStory

@register(VideoItem)
class VideoItemTranslationOptions(TranslationOptions):
    fields = ('title',)

@register(PhotoStory)
class PhotoStoryTranslationOptions(TranslationOptions):
    fields = ('title', 'description')
