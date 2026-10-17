from django.contrib import admin
from modeltranslation.admin import TranslationTabularInline
from apps.common.admin_base import BaseTranslatedAdmin
from .models import (
    Category, Author, Article, Tag, ArticleComment,
    BreakingNews, HomePagePlacement
)

class SubCategoryInline(TranslationTabularInline):
    model = Category
    fk_name = 'parent'
    extra = 1
    fields = ('name_en', 'name_ne', 'slug', 'order', 'show_in_menu')
    prepopulated_fields = {'slug': ('name_en',)}

@admin.register(Category)
class CategoryAdmin(BaseTranslatedAdmin):
    list_display = ('name_en', 'name_ne', 'slug', 'parent', 'order', 'show_in_menu', 'layout_type', 'translation_complete')
    list_filter = ('show_in_menu', 'layout_type', 'parent')
    search_fields = ('name_en', 'name_ne', 'slug')
    prepopulated_fields = {'slug': ('name_en',)}
    inlines = [SubCategoryInline]

    fieldsets = (
        ("Basic Setup", {
            "fields": ("name_en", "name_ne", "slug", "parent", "icon", "image"),
        }),
        ("Layout & Visibility", {
            "fields": ("layout_type", "order", "show_in_menu"),
        }),
        ("Description", {
            "fields": ("description_en", "description_ne"),
        }),
    )

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
            "fields": ("featuredImage", "imageCaption_en", "imageCaption_ne"),
        }),
        ("SEO & Meta Tags", {
            "fields": ("meta_title_en", "meta_title_ne", "meta_description_en", "meta_description_ne"),
        }),
    )

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
