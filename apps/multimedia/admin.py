from django.contrib import admin
from django.utils.safestring import mark_safe
from apps.common.admin_base import BaseTranslatedAdmin
from .models import VideoItem, VideoComment, PhotoStory, PhotoStoryImage, VideoLike, VideoCommentLike

@admin.register(VideoItem)
class VideoItemAdmin(BaseTranslatedAdmin):
    list_display = ('thumbnail_preview', 'title_en', 'district', 'duration', 'views', 'likes', 'isShort', 'publishedAt', 'translation_complete')
    list_display_links = ('thumbnail_preview', 'title_en')
    list_filter = ('isShort', 'district')
    search_fields = ('title_en', 'title_ne', 'youtube_id')
    readonly_fields = ('thumbnail_preview',)

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            url = obj.thumbnail.url if hasattr(obj.thumbnail, 'url') else str(obj.thumbnail)
            if not url.startswith(('http://', 'https://', '/')):
                url = f"/media/{url}"
            return mark_safe(f'<img src="{url}" style="width: 72px; height: 48px; object-fit: cover; border-radius: 4px; border: 1px solid #ddd;" />')
        return "-"
    thumbnail_preview.short_description = "Thumbnail"


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
