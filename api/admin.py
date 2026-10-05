from django import forms
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm
from django.utils.html import format_html
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline
from .utils import validate_phone_number, generate_username_from_phone
from .models import (
    Category, Author, District, Article, Tag, ArticleComment,
    VideoItem, PhotoStory, BreakingNews, Partner, HomePagePlacement,
    DistrictTheme, DistrictStats, DistrictCulture, DistrictPlace,
    UserProfile, DistrictSliderImage,
    Amenity, Hotel, HotelRoom, HotelGallery, HotelNearbyPlace
)

class BaseTranslatedAdmin(TranslationAdmin):
    """
    Base TranslationAdmin that:
    - Sets English and Nepali translation support.
    - Makes _en fields required (if base field not blank).
    - Makes _ne fields optional.
    - Provides a translation_complete column for list views.
    """
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for field_name, field in form.base_fields.items():
            if field_name.endswith('_en'):
                base_name = field_name[:-3]
                try:
                    base_field = self.model._meta.get_field(base_name)
                    if not getattr(base_field, 'blank', False):
                        field.required = True
                    verbose = base_field.verbose_name.title()
                    field.label = f"{verbose} (English)"
                except Exception:
                    pass
            elif field_name.endswith('_ne'):
                field.required = False
                base_name = field_name[:-3]
                try:
                    base_field = self.model._meta.get_field(base_name)
                    verbose = base_field.verbose_name.title()
                    field.label = f"{verbose} (नेपाली)"
                except Exception:
                    pass
        return form

    @admin.display(description="Nepali Translated", boolean=True)
    def translation_complete(self, obj):
        for attr in ('title_ne', 'name_ne', 'text_ne'):
            if hasattr(obj, attr):
                val = getattr(obj, attr)
                return bool(val and str(val).strip())
        return False


class SubCategoryInline(TranslationTabularInline):
    model = Category
    fk_name = 'parent'
    extra = 0
    fields = ('name_en', 'name_ne', 'slug', 'image', 'order', 'show_in_menu')
    prepopulated_fields = {'slug': ('name_en',)}
    verbose_name = "Sub-category"
    verbose_name_plural = "Sub-categories (shown as image strip under this menu item)"


@admin.register(Category)
class CategoryAdmin(BaseTranslatedAdmin):
    list_display = ('menu_label', 'name_ne', 'slug', 'parent', 'layout_type', 'order', 'show_in_menu', 'image_preview', 'translation_complete')
    list_display_links = ('menu_label',)
    list_editable = ('order', 'show_in_menu')
    list_filter = ('show_in_menu', ('parent', admin.RelatedOnlyFieldListFilter))
    search_fields = ('name_en', 'name_ne', 'slug')
    list_select_related = ('parent',)
    prepopulated_fields = {'slug': ('name_en',)}
    fieldsets = (
        ("Basic Setup", {
            "fields": (
                "name_en",
                "name_ne",
                "slug",
                "parent",
            ),
            "description": "Start here: Name your category and choose if it sits inside a parent category.",
        }),
        ("Visuals & Ordering", {
            "fields": (
                "layout_type",
                "image",
                "order",
                "show_in_menu",
            ),
            "description": "Upload a thumbnail image (for sub-categories) and control menu ordering.",
        }),
    )

    def get_inlines(self, request, obj=None):
        # Sub-categories can only be added to top-level categories
        if obj is None or obj.parent_id is None:
            return [SubCategoryInline]
        return []

    def get_queryset(self, request):
        # Show parents first, each followed by its children
        return super().get_queryset(request).order_by('parent__order', 'parent_id', 'order', 'id')

    @admin.display(description="Name", ordering='name_en')
    def menu_label(self, obj):
        if obj.parent_id:
            return format_html('<span style="color:#888;">↳</span> {}', obj.name_en or obj.slug)
        return format_html('<strong>{}</strong>', obj.name_en or obj.slug)

    @admin.display(description="Image Preview")
    def image_preview(self, obj):
        if obj.image:
            try:
                return format_html('<img src="{}" style="width: 28px; height: 28px; object-fit: cover; border-radius: 50%;" />', obj.image.url)
            except Exception:
                return str(obj.image)
        return "-"


@admin.register(Author)
class AuthorAdmin(BaseTranslatedAdmin):
    list_display = ('name_en', 'name_ne', 'slug', 'role', 'district', 'translation_complete')
    search_fields = ('name_en', 'name_ne', 'slug')
    list_filter = ('role', 'district')
    prepopulated_fields = {'slug': ('name_en',)}
    fieldsets = (
        ("Author Profile", {
            "fields": (
                "name_en",
                "name_ne",
                "slug",
                "role",
                "district",
                "avatar",
                "bio_en",
                "bio_ne",
            ),
        }),
    )


@admin.register(District)
class DistrictAdmin(BaseTranslatedAdmin):
    list_display = ('name_en', 'name_ne', 'slug', 'translation_complete')
    search_fields = ('name_en', 'name_ne', 'slug')
    fieldsets = (
        ("District Overview", {
            "fields": (
                "name_en",
                "name_ne",
                "slug",
                "description_en",
                "description_ne",
            ),
        }),
        ("Geographic & Appearance", {
            "fields": (
                "accentColor",
                "heroImage",
                "latitude",
                "longitude",
            ),
        }),
        ("SEO Metadata", {
            "fields": (
                "meta_title_en",
                "meta_title_ne",
                "meta_description_en",
                "meta_description_ne",
            ),
        }),
    )
    inlines = []


class DistrictSliderImageInline(admin.TabularInline):
    model = DistrictSliderImage
    extra = 1
    fields = ('image', 'caption_en', 'caption_ne', 'order')


DistrictAdmin.inlines = [DistrictSliderImageInline]



class TagInline(admin.TabularInline):
    model = Tag
    extra = 1


@admin.register(Article)
class ArticleAdmin(BaseTranslatedAdmin):
    list_display = ('title_en', 'category', 'author', 'district', 'status', 'publishedAt', 'translation_complete')
    list_filter = ('status', 'category', 'district', 'featured', 'breaking', 'popular')
    search_fields = ('title_en', 'title_ne', 'slug')
    prepopulated_fields = {'slug': ('title_en',)}
    inlines = [TagInline]
    fieldsets = (
        ("Content & Translation", {
            "fields": (
                "title_en",
                "title_ne",
                "slug",
                "excerpt_en",
                "excerpt_ne",
                "content_en",
                "content_ne",
            ),
        }),
        ("Categorization & Publishing", {
            "fields": (
                "category",
                "district",
                "author",
                "status",
                "publishedAt",
                "featured",
                "breaking",
                "popular",
                "readTime",
                "views",
                "likes",
            ),
        }),
        ("Media & Visuals", {
            "fields": (
                "featuredImage",
                "imageCaption_en",
                "imageCaption_ne",
            ),
        }),
        ("SEO Metadata", {
            "fields": (
                "meta_title_en",
                "meta_title_ne",
                "meta_description_en",
                "meta_description_ne",
            ),
        }),
    )


@admin.register(ArticleComment)
class ArticleCommentAdmin(admin.ModelAdmin):
    list_display = ('authorName', 'article', 'parent', 'createdAt', 'likes', 'user')
    search_fields = ('authorName', 'content')
    list_filter = ('createdAt',)
    raw_id_fields = ('parent', 'article', 'user')


@admin.register(VideoItem)
class VideoItemAdmin(BaseTranslatedAdmin):
    list_display = ('title_en', 'title_ne', 'district', 'publishedAt', 'views', 'isShort', 'translation_complete')
    list_filter = ('district', 'isShort')
    fieldsets = (
        ("Video Information", {
            "fields": (
                "title_en",
                "title_ne",
                "district",
                "isShort",
                "thumbnail",
                "duration",
                "views",
                "publishedAt",
            ),
        }),
    )


@admin.register(PhotoStory)
class PhotoStoryAdmin(BaseTranslatedAdmin):
    list_display = ('title_en', 'title_ne', 'district', 'photographer', 'imageCount', 'publishedAt', 'translation_complete')
    list_filter = ('district',)
    fieldsets = (
        ("Story Information", {
            "fields": (
                "title_en",
                "title_ne",
                "district",
                "photographer",
                "description_en",
                "description_ne",
                "coverImage",
                "imageCount",
                "publishedAt",
            ),
        }),
    )


@admin.register(BreakingNews)
class BreakingNewsAdmin(BaseTranslatedAdmin):
    list_display = ('text_en', 'text_ne', 'publishedAt', 'translation_complete')
    list_filter = ('publishedAt',)
    fieldsets = (
        ("Breaking News Alert", {
            "fields": (
                "text_en",
                "text_ne",
                "href",
            ),
        }),
    )


@admin.register(Partner)
class PartnerAdmin(BaseTranslatedAdmin):
    list_display = ('name_en', 'name_ne', 'role_en', 'role_ne', 'district', 'image_preview', 'translation_complete')
    list_filter = ('district',)
    readonly_fields = ('image_preview',)
    fieldsets = (
        ("Partner Organization", {
            "fields": (
                "name_en",
                "name_ne",
                "role_en",
                "role_ne",
                "district",
                "image",
                "image_preview",
                "url",
            ),
        }),
    )

    @admin.display(description="Logo / Image Preview")
    def image_preview(self, obj):
        if obj.image:
            try:
                if hasattr(obj.image, 'storage') and not obj.image.storage.exists(obj.image.name):
                    return format_html('<span style="color: #888; font-size: 11px; font-style: italic;">No file on disk</span>')
                return format_html(
                    '<img src="{}" style="height: 36px; max-width: 80px; object-fit: contain; border-radius: 4px; border: 1px solid #444; padding: 2px; background: #1a1a1a;" />',
                    obj.image.url
                )
            except Exception:
                return str(obj.image)
        return "-"


@admin.register(HomePagePlacement)
class HomePagePlacementAdmin(admin.ModelAdmin):
    list_display = ('section_name',)
    filter_horizontal = ('articles',)


@admin.register(DistrictTheme)
class DistrictThemeAdmin(admin.ModelAdmin):
    list_display = ('district', 'primary', 'dark', 'light')


@admin.register(DistrictStats)
class DistrictStatsAdmin(BaseTranslatedAdmin):
    list_display = ('district', 'headquarters_en', 'population', 'area', 'translation_complete')
    fieldsets = (
        ("Demographics & Geography", {
            "fields": (
                "district",
                "area",
                "population",
                "elevation",
                "headquarters_en",
                "headquarters_ne",
                "majorRivers_en",
                "majorRivers_ne",
                "literacy",
            ),
        }),
        ("Local Governance", {
            "fields": (
                "palikas_total",
                "palikas_municipalities",
                "palikas_rural",
            ),
        }),
    )


@admin.register(DistrictCulture)
class DistrictCultureAdmin(BaseTranslatedAdmin):
    list_display = ('district', 'translation_complete')
    fieldsets = (
        ("Cultural Heritage", {
            "fields": (
                "district",
                "folkDance_en",
                "folkDance_ne",
                "festivals_en",
                "festivals_ne",
                "cuisine_en",
                "cuisine_ne",
                "dialects_en",
                "dialects_ne",
            ),
        }),
    )


@admin.register(DistrictPlace)
class DistrictPlaceAdmin(BaseTranslatedAdmin):
    list_display = ('title_en', 'title_ne', 'district', 'category', 'translation_complete')
    list_filter = ('district', 'category')
    fieldsets = (
        ("Place Details", {
            "fields": (
                "district",
                "title_en",
                "title_ne",
                "category",
                "highlight",
                "image",
                "description_en",
                "description_ne",
            ),
        }),
    )


class CustomAdminUserCreationForm(AdminUserCreationForm):
    phone = forms.CharField(
        label="Phone Number",
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. 9841234567', 'autofocus': True}),
        help_text="Required. 7 to 15 digits."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].required = False
        self.fields['username'].help_text = "Optional. If left blank, username will be automatically generated from phone number."

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        cleaned = validate_phone_number(phone)
        if UserProfile.objects.filter(phone=cleaned).exists():
            raise forms.ValidationError("A user with this phone number already exists.")
        return cleaned

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get('phone')
        username = cleaned_data.get('username')
        if phone and not username:
            generated = generate_username_from_phone(phone)
            cleaned_data['username'] = generated
            self.instance.username = generated
            if 'username' in self._errors:
                del self._errors['username']
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        username = self.cleaned_data.get('username')
        if username:
            user.username = username
        if commit:
            user.save()
            phone = self.cleaned_data.get('phone')
            UserProfile.objects.update_or_create(user=user, defaults={'phone': phone})
        return user


class CustomUserChangeForm(UserChangeForm):
    phone = forms.CharField(
        label="Phone Number",
        max_length=20,
        required=True,
        help_text="Required. 7 to 15 digits."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            profile = getattr(self.instance, 'profile', None)
            if profile:
                self.fields['phone'].initial = profile.phone

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        cleaned = validate_phone_number(phone)
        qs = UserProfile.objects.filter(phone=cleaned)
        if self.instance and self.instance.pk:
            qs = qs.exclude(user=self.instance)
        if qs.exists():
            raise forms.ValidationError("A user with this phone number already exists.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=commit)
        phone = self.cleaned_data.get('phone')
        if phone:
            UserProfile.objects.update_or_create(user=user, defaults={'phone': phone})
        return user


try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    add_form = CustomAdminUserCreationForm
    form = CustomUserChangeForm

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'username', 'usable_password', 'password1', 'password2'),
        }),
    )

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    list_display = ('username', 'get_phone', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'profile__phone')

    @admin.display(description="Phone Number", ordering='profile__phone')
    def get_phone(self, obj):
        profile = getattr(obj, 'profile', None)
        return profile.phone if profile and profile.phone else "-"

# --- Hotel & Stay Admin ---

@admin.register(Amenity)
class AmenityAdmin(BaseTranslatedAdmin):
    list_display = ('name_en', 'name_ne', 'icon', 'translation_complete')
    search_fields = ('name_en', 'name_ne')

class HotelRoomInline(TranslationTabularInline):
    model = HotelRoom
    extra = 1
    fields = ('name_en', 'name_ne', 'guests', 'bed_type_en', 'bed_type_ne', 'price', 'image')

class HotelGalleryInline(TranslationTabularInline):
    model = HotelGallery
    extra = 1
    fields = ('image', 'caption_en', 'caption_ne')

class HotelNearbyPlaceInline(TranslationTabularInline):
    model = HotelNearbyPlace
    extra = 1
    fields = ('name_en', 'name_ne', 'distance_en', 'distance_ne')

@admin.register(Hotel)
class HotelAdmin(BaseTranslatedAdmin):
    list_display = ('name_en', 'category', 'district', 'rating', 'translation_complete')
    list_filter = ('category', 'district', 'hotel_type')
    search_fields = ('name_en', 'name_ne', 'slug')
    prepopulated_fields = {'slug': ('name_en',)}
    filter_horizontal = ('amenities',)
    inlines = [HotelRoomInline, HotelGalleryInline, HotelNearbyPlaceInline]
    
    fieldsets = (
        ("Basic Setup", {
            "fields": (
                "name_en", "name_ne", "slug", "category", "district", "hotel_type",
                "hero_image"
            ),
        }),
        ("Location & Rating", {
            "fields": (
                "address_en", "address_ne", "municipality_en", "municipality_ne",
                "latitude", "longitude", "rating", "reviews_count"
            ),
        }),
        ("Details", {
            "fields": (
                "about_en", "about_ne", "story_en", "story_ne",
                "highlights", "amenities"
            ),
        }),
        ("Contact & Reach", {
            "fields": (
                "phone1", "phone2", "email", "website", 
                "facebook_url", "instagram_url",
                "map_url", "reach_bus_en", "reach_bus_ne", 
                "reach_airport_en", "reach_airport_ne", 
                "reach_highway_en", "reach_highway_ne"
            ),
        }),
    )
