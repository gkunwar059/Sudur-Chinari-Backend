from django.contrib import admin
from apps.common.admin_base import BaseTranslatedAdmin
from .models import ProductCategory, LocalProduct, ProductProducer

@admin.register(ProductCategory)
class ProductCategoryAdmin(BaseTranslatedAdmin):
    list_display = ('name', 'slug', 'icon', 'order', 'is_active', 'translation_complete')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order', 'is_active')


@admin.register(LocalProduct)
class LocalProductAdmin(BaseTranslatedAdmin):
    list_display = ('name', 'category', 'district', 'farmer_name', 'status', 'is_verified', 'is_featured', 'translation_complete')
    list_filter = ('status', 'is_verified', 'category', 'district', 'is_featured')
    search_fields = ('name_en', 'name_ne', 'farmer_name', 'contact_phone', 'description_en', 'description_ne')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('status', 'is_verified', 'is_featured')

    @admin.action(description="Approve selected products")
    def approve_products(self, request, queryset):
        updated = queryset.update(status='approved', is_verified=True)
        self.message_user(request, f"{updated} products approved and marked as verified.")

    @admin.action(description="Reject selected products")
    def reject_products(self, request, queryset):
        updated = queryset.update(status='rejected', is_verified=False)
        self.message_user(request, f"{updated} products marked as rejected.")

    actions = ['approve_products', 'reject_products']


@admin.register(ProductProducer)
class ProductProducerAdmin(BaseTranslatedAdmin):
    list_display = ('name', 'district', 'municipality_address', 'phone', 'experience_years', 'is_verified', 'translation_complete')
    list_filter = ('district', 'is_verified')
    search_fields = ('name_en', 'name_ne', 'phone', 'municipality_address_en', 'municipality_address_ne')


