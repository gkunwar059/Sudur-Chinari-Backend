from django.contrib import admin
from django.contrib import messages
from django.db import models
from apps.common.admin_base import BaseTranslatedAdmin
from .models import ProductCategory, LocalProduct, ProductProducer, SYSTEM_PRODUCT_SLUGS

@admin.register(ProductCategory)
class ProductCategoryAdmin(BaseTranslatedAdmin):
    list_display = ('name', 'slug', 'icon', 'order', 'is_active', 'is_system', 'translation_complete')
    list_filter = ('is_system', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order', 'is_active')

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if obj and (getattr(obj, 'is_system', False) or obj.slug in SYSTEM_PRODUCT_SLUGS):
            if 'slug' not in readonly:
                readonly.append('slug')
            if 'is_system' not in readonly:
                readonly.append('is_system')
        return readonly

    def has_delete_permission(self, request, obj=None):
        if obj and (getattr(obj, 'is_system', False) or obj.slug in SYSTEM_PRODUCT_SLUGS):
            return False
        return super().has_delete_permission(request, obj)

    def delete_queryset(self, request, queryset):
        system_items = queryset.filter(models.Q(is_system=True) | models.Q(slug__in=SYSTEM_PRODUCT_SLUGS))
        if system_items.exists():
            names = ", ".join(system_items.values_list('slug', flat=True))
            self.message_user(
                request,
                f"Action blocked: Cannot delete protected product categories ({names}).",
                level=messages.ERROR
            )
            queryset = queryset.exclude(models.Q(is_system=True) | models.Q(slug__in=SYSTEM_PRODUCT_SLUGS))
        super().delete_queryset(request, queryset)



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


