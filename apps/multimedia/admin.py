from django.contrib import admin
from apps.common.admin_base import BaseTranslatedAdmin
from .models import VideoItem, PhotoStory

@admin.register(VideoItem)
class VideoItemAdmin(BaseTranslatedAdmin):
    list_display = ('title_en', 'district', 'duration', 'views', 'isShort', 'publishedAt', 'translation_complete')
    list_filter = ('isShort', 'district')
    search_fields = ('title_en', 'title_ne')

@admin.register(PhotoStory)
class PhotoStoryAdmin(BaseTranslatedAdmin):
    list_display = ('title_en', 'photographer', 'district', 'imageCount', 'publishedAt', 'translation_complete')
    list_filter = ('district',)
    search_fields = ('title_en', 'title_ne', 'photographer')
