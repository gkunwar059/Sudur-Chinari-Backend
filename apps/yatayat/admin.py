from django.contrib import admin
from apps.common.admin_base import BaseTranslatedAdmin
from .models import (
    TransportLocation, TransportService,
    TransportReport, EmergencyHelpline
)

@admin.register(TransportLocation)
class TransportLocationAdmin(BaseTranslatedAdmin):
    list_display = ('name', 'district', 'is_hub', 'phone', 'helpdesk_contact', 'translation_complete')
    list_filter = ('is_hub', 'district')
    search_fields = ('name_en', 'name_ne', 'phone')


@admin.register(TransportService)
class TransportServiceAdmin(BaseTranslatedAdmin):
    list_display = (
        'title', 'service_type', 'origin_name', 'destination_name',
        'departure_time', 'estimated_fare', 'contact_phone',
        'status', 'verified', 'is_active', 'translation_complete'
    )
    list_filter = ('status', 'service_type', 'verified', 'is_active', 'badge_color')
    search_fields = (
        'title_en', 'title_ne', 'origin_name_en', 'origin_name_ne',
        'destination_name_en', 'destination_name_ne', 'contact_phone'
    )
    list_editable = ('status', 'verified', 'is_active')

    @admin.action(description="Approve selected transport services")
    def approve_services(self, request, queryset):
        updated = queryset.update(status='approved', verified=True, is_active=True)
        self.message_user(request, f"{updated} transport services approved and published.")

    @admin.action(description="Reject selected transport services")
    def reject_services(self, request, queryset):
        updated = queryset.update(status='rejected', verified=False, is_active=False)
        self.message_user(request, f"{updated} transport services marked as rejected.")

    actions = ['approve_services', 'reject_services']


@admin.register(TransportReport)
class TransportReportAdmin(admin.ModelAdmin):
    list_display = ('service', 'issue_type', 'reporter_phone', 'created_at')
    list_filter = ('issue_type', 'created_at')
    search_fields = ('description', 'reporter_phone')


@admin.register(EmergencyHelpline)
class EmergencyHelplineAdmin(BaseTranslatedAdmin):
    list_display = ('title', 'category', 'district', 'phone_number', 'is_24_7', 'order', 'translation_complete')
    list_filter = ('category', 'is_24_7', 'district')
    search_fields = ('title_en', 'title_ne', 'phone_number')
