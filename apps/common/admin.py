from django.contrib import admin
from apps.common.admin_base import BaseTranslatedAdmin
from .models import TrendingTopic, ContactInquiry, NewsletterSubscriber

@admin.register(TrendingTopic)
class TrendingTopicAdmin(BaseTranslatedAdmin):
    list_display = ('name_en', 'name_ne', 'slug', 'search_count', 'order', 'is_active', 'translation_complete')
    list_filter = ('is_active',)
    search_fields = ('name_en', 'name_ne', 'slug')
    prepopulated_fields = {'slug': ('name_en',)}
    list_editable = ('order', 'is_active')


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'email', 'phone', 'inquiry_type', 'created_at')
    list_filter = ('inquiry_type', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('email',)
