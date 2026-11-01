from django.contrib import admin
from apps.common.admin_base import BaseTranslatedAdmin
from .models import VideoItem, VideoComment, PhotoStory, PhotoStoryImage, VideoLike, VideoCommentLike

@admin.register(VideoItem)
class VideoItemAdmin(BaseTranslatedAdmin):
    list_display = ('title_en', 'district', 'duration', 'views', 'likes', 'isShort', 'publishedAt', 'translation_complete')
    list_filter = ('isShort', 'district')
    search_fields = ('title_en', 'title_ne', 'youtube_id')


@admin.register(VideoComment)
class VideoCommentAdmin(admin.ModelAdmin):
    list_display = ('authorName', 'video', 'likes', 'createdAt')
    list_filter = ('createdAt',)
    search_fields = ('authorName', 'content')


@admin.register(VideoLike)
class VideoLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'video', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'video__title')


@admin.register(VideoCommentLike)
class VideoCommentLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'comment__content')


class PhotoStoryImageInline(admin.TabularInline):
    model = PhotoStoryImage
    extra = 2


@admin.register(PhotoStory)
class PhotoStoryAdmin(BaseTranslatedAdmin):
    list_display = ('title_en', 'photographer', 'district', 'imageCount', 'publishedAt', 'translation_complete')
    list_filter = ('district',)
    search_fields = ('title_en', 'title_ne', 'photographer')
    inlines = [PhotoStoryImageInline]


@admin.register(PhotoStoryImage)
class PhotoStoryImageAdmin(BaseTranslatedAdmin):
    list_display = ('story', 'caption_en', 'order', 'created_at', 'translation_complete')
    list_filter = ('story',)
