from django.contrib import admin
from django.utils.html import format_html
from apps.common.admin_base import BaseTranslatedAdmin
from .models import PopupAd, BannerAd

@admin.register(PopupAd)
class PopupAdAdmin(BaseTranslatedAdmin):
    list_display = ('title_en', 'advertiser', 'duration_seconds', 'is_active', 'created_at', 'translation_complete')
    list_filter = ('is_active',)
    search_fields = ('title_en', 'title_ne', 'advertiser')


@admin.register(BannerAd)
class BannerAdAdmin(admin.ModelAdmin):
    list_display = (
        'image_thumbnail',
        'title',
        'page_badge',
        'placement_badge',
        'advertiser_display',
        'status',
        'is_active',
        'priority',
        'clicks_count',
        'impressions_count',
        'created_at'
    )
    list_filter = (
        'status',
        'page',
        'placement',
        'is_active',
        'start_date',
        'end_date',
        'created_at'
    )
    search_fields = (
        'title',
        'advertiser',
        'contact_name',
        'contact_email',
        'contact_phone',
        'target_url',
        'notes',
        'custom_page_path'
    )
    list_editable = ('status', 'is_active', 'priority')
    readonly_fields = (
        'image_preview_large',
        'clicks_count',
        'impressions_count',
        'created_at',
        'updated_at'
    )
    actions = [
        'approve_and_activate',
        'reject_ads',
        'activate_ads',
        'deactivate_ads'
    ]

    fieldsets = (
        ("🎯 Page & Placement Targeting (पूर्ण नियन्त्रण)", {
            "description": "कुन पृष्ठ र कुन स्थानमा विज्ञापन देखाउने यहाँबाट पूर्ण नियन्त्रण गर्नुहोस्।",
            "fields": (
                ("page", "custom_page_path"),
                ("placement", "priority"),
            )
        }),
        ("🎨 Ad Creative & Details (विज्ञापन सामाग्री)", {
            "fields": (
                "title",
                ("image", "image_url"),
                "image_preview_large",
                "target_url",
                "alt_text",
                "advertiser",
            )
        }),
        ("🛡️ Status & Verification (प्रमाणीकरण तथा स्थिति)", {
            "fields": (
                ("status", "is_active"),
                "rejection_reason",
            )
        }),
        ("📅 Campaign Schedule (समयावधि)", {
            "fields": (
                ("start_date", "end_date"),
            )
        }),
        ("👤 Submitter / Advertiser Contact (अनुरोधकर्ता विवरण)", {
            "classes": ("collapse",),
            "fields": (
                "requested_by",
                ("contact_name", "contact_phone"),
                "contact_email",
                "notes",
            )
        }),
        ("📊 Analytics & History (तथ्यांक)", {
            "classes": ("collapse",),
            "fields": (
                ("clicks_count", "impressions_count"),
                ("created_at", "updated_at"),
            )
        }),
    )

    def image_thumbnail(self, obj):
        url = obj.image.url if obj.image else obj.image_url
        if url:
            return format_html(
                '<a href="{0}" target="_blank" title="View Full Image">'
                '<img src="{0}" style="height: 40px; max-width: 90px; object-fit: cover; border-radius: 4px; border: 1px solid #cbd5e1; box-shadow: 0 1px 2px rgba(0,0,0,0.05);" />'
                '</a>',
                url
            )
        return format_html('<span style="color: #94a3b8; font-size: 11px;">[No Image]</span>')
    image_thumbnail.short_description = "Preview"

    def image_preview_large(self, obj):
        url = obj.image.url if obj.image else obj.image_url
        if url:
            return format_html(
                '<div style="margin-top: 8px;">'
                '<img src="{0}" style="max-height: 180px; max-width: 100%; object-fit: contain; border-radius: 6px; border: 1px solid #cbd5e1; padding: 4px; background: #f8fafc;" />'
                '</div>',
                url
            )
        return "No image uploaded yet"
    image_preview_large.short_description = "Live Creative Preview"

    def page_badge(self, obj):
        return format_html(
            '<span style="background: #f1f5f9; color: #334155; padding: 3px 8px; border-radius: 4px; font-weight: 600; font-size: 11px; border: 1px solid #e2e8f0; white-space: nowrap;">'
            '📄 {0}'
            '</span>',
            obj.get_page_display().split(' (')[0]
        )
    page_badge.short_description = "Target Page"

    def placement_badge(self, obj):
        return format_html(
            '<span style="background: #ecfdf5; color: #047857; padding: 3px 8px; border-radius: 4px; font-weight: 600; font-size: 11px; border: 1px solid #a7f3d0; white-space: nowrap;">'
            '📍 {0}'
            '</span>',
            obj.get_placement_display().split(' (')[0]
        )
    placement_badge.short_description = "Position"

    def advertiser_display(self, obj):
        adv = obj.advertiser or obj.contact_name or "Self"
        req = f" ({obj.requested_by.username})" if obj.requested_by else ""
        return f"{adv}{req}"
    advertiser_display.short_description = "Advertiser"

    def status_badge(self, obj):
        colors = {
            'approved': ('#059669', '#ecfdf5', '#a7f3d0'),  # Emerald
            'pending': ('#d97706', '#fffbeb', '#fde68a'),   # Amber
            'rejected': ('#dc2626', '#fef2f2', '#fecaca'),  # Red
        }
        color, bg, border = colors.get(obj.status, ('#64748b', '#f8fafc', '#e2e8f0'))
        return format_html(
            '<span style="background-color: {0}; color: {1}; border: 1px solid {2}; padding: 3px 9px; border-radius: 12px; font-weight: 700; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;">'
            '{3}'
            '</span>',
            bg, color, border, obj.get_status_display().split(' (')[0]
        )
    status_badge.short_description = "Status"

    @admin.action(description="✅ Approve and activate selected ads (प्रमाणित गरी प्रकाशित गर्नुहोस्)")
    def approve_and_activate(self, request, queryset):
        count = queryset.update(status='approved', is_active=True, rejection_reason="")
        self.message_user(request, f"{count} advertisement(s) approved and activated successfully.")

    @admin.action(description="❌ Reject selected ads (अस्वीकृत गर्नुहोस्)")
    def reject_ads(self, request, queryset):
        count = queryset.update(status='rejected', is_active=False)
        self.message_user(request, f"{count} advertisement(s) rejected.")

    @admin.action(description="🟢 Mark as Active (सक्रिय बनाउनुहोस्)")
    def activate_ads(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count} advertisement(s) set to active.")

    @admin.action(description="⚪ Mark as Inactive (निष्क्रिय बनाउनुहोस्)")
    def deactivate_ads(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count} advertisement(s) set to inactive.")

