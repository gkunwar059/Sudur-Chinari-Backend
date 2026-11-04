from django.contrib import admin
from django.db import models
from django.contrib import messages
from modeltranslation.admin import TranslationTabularInline
from apps.common.admin_base import BaseTranslatedAdmin
from .models import (
    Category, Author, Article, Tag, ArticleComment,
    BreakingNews, HomePagePlacement, ArticleBookmark, HeroSlide,
    SYSTEM_SLUGS
)

class SubCategoryInline(TranslationTabularInline):
    model = Category
    fk_name = 'parent'
    extra = 1
    fields = ('name_en', 'name_ne', 'slug', 'order', 'show_in_menu')
    prepopulated_fields = {'slug': ('name_en',)}

@admin.register(Category)
class CategoryAdmin(BaseTranslatedAdmin):
    list_display = ('name_en', 'name_ne', 'slug', 'is_system', 'parent', 'order', 'show_in_menu', 'layout_type', 'translation_complete')
    list_filter = ('is_system', 'show_in_menu', 'layout_type', 'parent')
    search_fields = ('name_en', 'name_ne', 'slug')
    prepopulated_fields = {'slug': ('name_en',)}
    inlines = [SubCategoryInline]

    fieldsets = (
        ("Basic Setup", {
            "fields": ("name_en", "name_ne", "slug", "is_system", "parent", "icon", "image"),
        }),
        ("Layout & Visibility", {
            "fields": ("layout_type", "order", "show_in_menu"),
        }),
        ("Description", {
            "fields": ("description",),
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if obj and (obj.is_system or obj.slug in SYSTEM_SLUGS):
            if 'slug' not in readonly:
                readonly.append('slug')
            if 'is_system' not in readonly:
                readonly.append('is_system')
        return readonly

    def has_delete_permission(self, request, obj=None):
        if obj and (obj.is_system or obj.slug in SYSTEM_SLUGS):
            return False
        return super().has_delete_permission(request, obj)

    def delete_queryset(self, request, queryset):
        system_items = queryset.filter(models.Q(is_system=True) | models.Q(slug__in=SYSTEM_SLUGS))
        if system_items.exists():
            names = ", ".join(system_items.values_list('slug', flat=True))
            self.message_user(
                request,
                f"Action blocked: Cannot delete protected system categories ({names}).",
                level=messages.ERROR
            )
            queryset = queryset.exclude(models.Q(is_system=True) | models.Q(slug__in=SYSTEM_SLUGS))
        super().delete_queryset(request, queryset)

    def get_queryset(self, request):
        return super().get_queryset(request).filter(parent__isnull=True)


class TagInline(admin.TabularInline):
    model = Tag
    extra = 1

class ArticleCommentInline(admin.TabularInline):
    model = ArticleComment
    extra = 0
    readonly_fields = ('user', 'authorName', 'authorLocation', 'content', 'createdAt', 'likes')
    can_delete = True

@admin.register(Author)
class AuthorAdmin(BaseTranslatedAdmin):
    list_display = ('name_en', 'name_ne', 'role_en', 'district', 'translation_complete')
    search_fields = ('name_en', 'name_ne', 'slug', 'role_en', 'role_ne')
    prepopulated_fields = {'slug': ('name_en',)}

@admin.register(Article)
class ArticleAdmin(BaseTranslatedAdmin):
    list_display = ('title_en', 'category', 'author', 'district', 'status', 'publishedAt', 'views', 'translation_complete')
    list_filter = ('status', 'featured', 'breaking', 'popular', 'category', 'district', 'publishedAt')
    search_fields = ('title_en', 'title_ne', 'content_en', 'content_ne', 'slug')
    prepopulated_fields = {'slug': ('title_en',)}
    readonly_fields = ('image_preview',)
    inlines = [TagInline, ArticleCommentInline]

    fieldsets = (
        ("Header & Slug", {
            "fields": ("title_en", "title_ne", "slug", "category", "author", "district"),
        }),
        ("Status & Workflow", {
            "fields": ("status", "publishedAt", "featured", "breaking", "popular", "readTime", "views", "likes"),
        }),
        ("Lead & Summary", {
            "fields": ("excerpt_en", "excerpt_ne"),
        }),
        ("Article Body", {
            "fields": ("content_en", "content_ne"),
        }),
        ("Media & Visuals", {
            "fields": ("image", "featuredImage", "image_preview", "imageCaption_en", "imageCaption_ne"),
        }),
        ("SEO & Meta Tags", {
            "fields": ("meta_title_en", "meta_title_ne", "meta_description_en", "meta_description_ne"),
        }),
    )

    def image_preview(self, obj):
        from django.utils.html import format_html
        url = None
        if obj and obj.image:
            url = obj.image.url
        elif obj and obj.featuredImage:
            url = obj.featuredImage
        if url:
            return format_html(
                '<div style="margin-top: 4px;">'
                '<img src="{}" style="max-height: 180px; max-width: 320px; border-radius: 8px; border: 1px solid #cbd5e1; object-fit: cover; box-shadow: 0 1px 3px rgba(0,0,0,0.1);" />'
                '<br><span style="font-size: 12px; color: #64748b; font-weight: 500;">Active Cover Preview</span>'
                '</div>',
                url
            )
        return "No image uploaded yet"
    image_preview.short_description = "Image Preview"

@admin.register(ArticleComment)
class ArticleCommentAdmin(admin.ModelAdmin):
    list_display = ('authorName', 'article', 'createdAt', 'likes')
    list_filter = ('createdAt',)
    search_fields = ('authorName', 'content', 'article__title_en')

@admin.register(BreakingNews)
class BreakingNewsAdmin(BaseTranslatedAdmin):
    list_display = ('text_en', 'publishedAt', 'translation_complete')
    search_fields = ('text_en', 'text_ne')

@admin.register(HomePagePlacement)
class HomePagePlacementAdmin(admin.ModelAdmin):
    list_display = ('section_name',)
    filter_horizontal = ('articles',)


@admin.register(ArticleBookmark)
class ArticleBookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'article__title_en', 'article__title_ne')


@admin.register(HeroSlide)
class HeroSlideAdmin(BaseTranslatedAdmin):
    list_display = ('title_en', 'title_ne', 'subtitle_en', 'order', 'is_active', 'article', 'translation_complete')
    list_filter = ('is_active',)
    search_fields = ('title_en', 'title_ne', 'subtitle_en', 'subtitle_ne', 'excerpt_en', 'excerpt_ne')
    list_editable = ('order', 'is_active')

    fieldsets = (
        ("Content (Bilingual)", {
            "fields": (
                ("title_en", "title_ne"),
                ("subtitle_en", "subtitle_ne"),
                ("excerpt_en", "excerpt_ne"),
            )
        }),
        ("Media & Target", {
            "fields": (
                "image", "image_url", "article",
            )
        }),
        ("Call To Actions", {
            "fields": (
                ("primary_button_text_en", "primary_button_text_ne"),
                "primary_button_url",
                ("secondary_button_text_en", "secondary_button_text_ne"),
                "secondary_button_url",
            )
        }),
        ("Display Settings", {
            "fields": (
                "order", "is_active",
            )
        }),
    )
