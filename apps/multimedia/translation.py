from modeltranslation.translator import register, TranslationOptions
from .models import VideoItem, PhotoStory, PhotoStoryImage

@register(VideoItem)
class VideoItemTranslationOptions(TranslationOptions):
    fields = ('title',)

@register(PhotoStory)
class PhotoStoryTranslationOptions(TranslationOptions):
    fields = ('title', 'description')

@register(PhotoStoryImage)
class PhotoStoryImageTranslationOptions(TranslationOptions):
    fields = ('caption',)
