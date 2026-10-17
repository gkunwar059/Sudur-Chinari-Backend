from django.contrib import admin
from modeltranslation.admin import TranslationTabularInline, TranslationStackedInline
from apps.common.admin_base import BaseTranslatedAdmin
from .models import (
    District, DistrictTheme, DistrictStats, DistrictCulture,
    DistrictPlace, DistrictSliderImage, Partner
)

class DistrictThemeInline(admin.StackedInline):
    model = DistrictTheme
    can_delete = False
    verbose_name_plural = 'Theme Settings'

class DistrictStatsInline(TranslationStackedInline):
    model = DistrictStats
    can_delete = False
    verbose_name_plural = 'District Statistics'

class DistrictCultureInline(TranslationStackedInline):
    model = DistrictCulture
    can_delete = False
    verbose_name_plural = 'Cultural Information'

class DistrictPlaceInline(TranslationTabularInline):
    model = DistrictPlace
    extra = 1
    fields = ('title_en', 'title_ne', 'category', 'highlight', 'image')

class DistrictSliderImageInline(TranslationTabularInline):
    model = DistrictSliderImage
    extra = 1
    fields = ('image', 'caption_en', 'caption_ne', 'order')

class PartnerInline(TranslationTabularInline):
    model = Partner
    extra = 0
    fields = ('name_en', 'name_ne', 'role_en', 'role_ne', 'image', 'url')

@admin.register(District)
class DistrictAdmin(BaseTranslatedAdmin):
    list_display = ('name_en', 'name_ne', 'slug', 'accentColor', 'translation_complete')
    search_fields = ('name_en', 'name_ne', 'slug')
    prepopulated_fields = {'slug': ('name_en',)}
    inlines = [
        DistrictThemeInline,
        DistrictStatsInline,
        DistrictCultureInline,
        DistrictPlaceInline,
        DistrictSliderImageInline,
        PartnerInline
    ]
    fieldsets = (
        ("Basic Information", {
            "fields": ("name_en", "name_ne", "slug", "accentColor", "heroImage", "latitude", "longitude")
        }),
        ("Content", {
            "fields": ("description_en", "description_ne", "history_en", "history_ne")
        }),
        ("SEO / Meta", {
            "fields": ("meta_title_en", "meta_title_ne", "meta_description_en", "meta_description_ne")
        }),
    )

@admin.register(DistrictPlace)
class DistrictPlaceAdmin(BaseTranslatedAdmin):
    list_display = ('title_en', 'district', 'category', 'highlight', 'translation_complete')
    list_filter = ('district', 'category')
    search_fields = ('title_en', 'title_ne', 'district__name_en')

@admin.register(Partner)
class PartnerAdmin(BaseTranslatedAdmin):
    list_display = ('name_en', 'role_en', 'district', 'translation_complete')
    list_filter = ('district',)
    search_fields = ('name_en', 'name_ne', 'role_en', 'role_ne')
