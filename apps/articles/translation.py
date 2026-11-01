from modeltranslation.translator import register, TranslationOptions
from .models import Category, Author, Article, BreakingNews, HeroSlide

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Author)
class AuthorTranslationOptions(TranslationOptions):
    fields = ('name', 'role', 'bio')

@register(Article)
class ArticleTranslationOptions(TranslationOptions):
    fields = ('title', 'excerpt', 'content', 'imageCaption', 'meta_title', 'meta_description')

@register(BreakingNews)
class BreakingNewsTranslationOptions(TranslationOptions):
    fields = ('text',)

@register(HeroSlide)
class HeroSlideTranslationOptions(TranslationOptions):
    fields = ('title', 'subtitle', 'excerpt', 'primary_button_text', 'secondary_button_text')
