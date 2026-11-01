from modeltranslation.translator import register, TranslationOptions
from .models import ProductCategory, LocalProduct, ProductProducer

@register(ProductCategory)
class ProductCategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(LocalProduct)
class LocalProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'seasonality')

@register(ProductProducer)
class ProductProducerTranslationOptions(TranslationOptions):
    fields = ('name', 'municipality_address', 'bio')
