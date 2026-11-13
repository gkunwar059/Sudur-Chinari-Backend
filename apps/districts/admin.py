from django.contrib import admin
from modeltranslation.admin import TranslationTabularInline, TranslationStackedInline
from apps.common.admin_base import BaseTranslatedAdmin
from .models import (
    District, DistrictTheme, DistrictStats, DistrictCulture,
    DistrictPlace, DistrictSliderImage, Partner,
    PhotoSubmission, StorySubmission
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
    fields = ('title_en', 'title_ne', 'slug', 'category', 'highlight_en', 'highlight_ne', 'location_en', 'location_ne', 'image')

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
    list_display = ('title_en', 'slug', 'district', 'category', 'location_en', 'highlight_en', 'translation_complete')
    list_filter = ('district', 'category')
    search_fields = ('title_en', 'title_ne', 'slug', 'location_en', 'location_ne', 'district__name_en')
    prepopulated_fields = {'slug': ('title_en',)}
    fieldsets = (
        ("Basic Information", {
            "fields": (
                "district", "title_en", "title_ne", "slug", "category",
                "highlight_en", "highlight_ne", "image",
            )
        }),
        ("Description & Editorial Overview", {
            "fields": (
                "description_en", "description_ne",
                "overview_en", "overview_ne",
                "history_en", "history_ne",
            )
        }),
        ("Location, Geographic Facts & Access", {
            "fields": (
                "location_en", "location_ne",
                "elevation_en", "elevation_ne",
                "area_or_size_en", "area_or_size_ne",
                "best_time_to_visit_en", "best_time_to_visit_ne",
                "opening_hours_en", "opening_hours_ne",
                "entry_fee_en", "entry_fee_ne",
                "weather_summary_en", "weather_summary_ne",
                "how_to_reach_en", "how_to_reach_ne",
                "latitude", "longitude",
            )
        }),
        ("Local Culture, Cuisine & Traditions", {
            "fields": (
                "festivals_en", "festivals_ne",
                "local_cuisine_en", "local_cuisine_ne",
                "traditions_en", "traditions_ne",
                "languages_en", "languages_ne",
            )
        }),
        ("Travel Advisory & Visitor Tips", {
            "fields": (
                "travel_advisory_en", "travel_advisory_ne",
            )
        }),
    )

@admin.register(Partner)
class PartnerAdmin(BaseTranslatedAdmin):
    list_display = ('name_en', 'role_en', 'district', 'translation_complete')
    list_filter = ('district',)
    search_fields = ('name_en', 'name_ne', 'role_en', 'role_ne')


@admin.register(PhotoSubmission)
class PhotoSubmissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'photographer_name', 'district', 'status', 'created_at')
    list_filter = ('status', 'district', 'created_at')
    search_fields = ('title', 'photographer_name', 'description')
    list_editable = ('status',)
    actions = ['approve_photos', 'reject_photos']

    @admin.action(description='Approve selected photos (Show in frontend)')
    def approve_photos(self, request, queryset):
        count = queryset.update(status='approved')
        self.message_user(request, f"{count} photos approved successfully.")

    @admin.action(description='Reject selected photos')
    def reject_photos(self, request, queryset):
        count = queryset.update(status='rejected')
        self.message_user(request, f"{count} photos rejected.")


@admin.register(StorySubmission)
class StorySubmissionAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_name', 'district', 'main_category', 'status', 'created_at')
    list_filter = ('status', 'main_category', 'district', 'created_at')
    search_fields = ('title', 'author_name', 'description')
    list_editable = ('status',)
    actions = ['approve_stories', 'reject_stories']

    @admin.action(description='Approve selected stories (Show in frontend)')
    def approve_stories(self, request, queryset):
        count = queryset.update(status='approved')
        self.message_user(request, f"{count} stories approved successfully.")

    @admin.action(description='Reject selected stories')
    def reject_stories(self, request, queryset):
        count = queryset.update(status='rejected')
        self.message_user(request, f"{count} stories rejected.")
