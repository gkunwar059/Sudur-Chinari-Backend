from django.contrib import admin
from apps.common.admin_base import BaseTranslatedAdmin
from .models import PopupAd

@admin.register(PopupAd)
class PopupAdAdmin(BaseTranslatedAdmin):
    list_display = ('title_en', 'advertiser', 'duration_seconds', 'is_active', 'created_at', 'translation_complete')
    list_filter = ('is_active',)
    search_fields = ('title_en', 'title_ne', 'advertiser')
