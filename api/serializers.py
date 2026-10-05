from rest_framework import serializers
from rest_framework.settings import api_settings
from modeltranslation.translator import translator
from django.contrib.auth import get_user_model, password_validation
from django.core import exceptions as django_exceptions
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from core.middleware import get_requested_lang
from .utils import validate_phone_number, generate_username_from_phone
from .models import (
    Category, Author, District, Article, Tag, ArticleComment,
    VideoItem, PhotoStory, BreakingNews, Partner, HomePagePlacement,
    DistrictTheme, DistrictStats, DistrictCulture, DistrictPlace,
    UserProfile, DistrictSliderImage,
    Amenity, Hotel, HotelRoom, HotelGallery, HotelNearbyPlace
)

def make_absolute_url(url, request):
    """Returns an absolute URL for media and image paths."""
    if not url:
        return None
    if hasattr(url, 'url'):
        try:
            url = url.url
        except Exception:
            return None
    url_str = str(url)
    if not url_str:
        return None
    if url_str.startswith(('http://', 'https://')):
        return url_str
    if not url_str.startswith('/'):
        url_str = f"/media/{url_str}"
    if request:
        try:
            return request.build_absolute_uri(url_str)
        except Exception:
            pass
    return f"http://127.0.0.1:8001{url_str}"


class TranslatedAdminSerializerMixin:
    """
    Reusable serializer mixin that:
    1. Returns a single resolved value (e.g. name, description) for public requests using active language.
    2. ONLY when ?lang=all AND request.user.is_staff: includes _en and _ne fields for translatable fields.
    3. If ?lang=all is requested by non-staff/anonymous, ignores it and returns single-language shape.
    4. Write endpoints (create/update) for staff accept _en and _ne fields.
    5. Detail responses include 'lang' ('en'|'ne') and 'translation_missing' (boolean).
    6. Ensures image/media URLs are returned as absolute URLs.
    """

    def get_fields(self):
        fields = super().get_fields()
        model = getattr(getattr(self, 'Meta', None), 'model', None)
        if not model:
            return fields

        try:
            opts = translator.get_options_for_model(model)
        except Exception:
            opts = None

        if opts:
            for tf in opts.fields:
                for lang_code in ('en', 'ne'):
                    fname = f"{tf}_{lang_code}"
                    if fname not in fields:
                        # Register as write_only so default to_representation won't expose it
                        fields[fname] = serializers.CharField(
                            required=False,
                            allow_blank=True,
                            allow_null=True,
                            write_only=True
                        )
        return fields

    def to_internal_value(self, data):
        request = self.context.get('request')
        is_staff = bool(
            request and getattr(request, 'user', None) and
            request.user.is_authenticated and request.user.is_staff
        )

        # If user is not staff, strip any _en or _ne translation fields from input
        if not is_staff and request is not None and isinstance(data, dict):
            model = getattr(getattr(self, 'Meta', None), 'model', None)
            if model:
                try:
                    opts = translator.get_options_for_model(model)
                except Exception:
                    opts = None
                if opts:
                    data = data.copy()
                    for tf in opts.fields:
                        for lang_code in ('en', 'ne'):
                            data.pop(f"{tf}_{lang_code}", None)

        return super().to_internal_value(data)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get('request')
        is_staff = bool(
            request and getattr(request, 'user', None) and
            request.user.is_authenticated and request.user.is_staff
        )
        lang_all = bool(
            request and (
                getattr(request, 'lang_all', False) or
                (hasattr(request, 'query_params') and request.query_params.get('lang') == 'all') or
                (hasattr(request, 'GET') and request.GET.get('lang') == 'all')
            )
        )

        model = getattr(getattr(self, 'Meta', None), 'model', None)
        try:
            opts = translator.get_options_for_model(model) if model else None
        except Exception:
            opts = None

        # 1. Staff + ?lang=all gets explicit _en and _ne fields
        if is_staff and lang_all and opts:
            for tf in opts.fields:
                for lang_code in ('en', 'ne'):
                    fname = f"{tf}_{lang_code}"
                    if hasattr(instance, fname):
                        ret[fname] = getattr(instance, fname)

        # 2. Check if this is a top-level detail response
        is_detail = bool(
            self.context.get('is_detail') or
            (self.context.get('view') and getattr(self.context['view'], 'action', None) == 'retrieve') or
            (self.parent is None and not getattr(self, 'many', False))
        )

        if is_detail:
            if request:
                req_lang = get_requested_lang(request)
            else:
                from django.utils import translation
                req_lang = translation.get_language() or 'en'

            if req_lang == 'ne':
                # Check whether the primary text fields have a real Nepali translation
                has_ne = False
                for field_name in ('title_ne', 'name_ne', 'text_ne'):
                    if hasattr(instance, field_name):
                        val = getattr(instance, field_name)
                        if val and str(val).strip():
                            has_ne = True
                            break
                if has_ne:
                    ret['lang'] = 'ne'
                    ret['translation_missing'] = False
                else:
                    ret['lang'] = 'en'
                    ret['translation_missing'] = True
            else:
                ret['lang'] = 'en'
                ret['translation_missing'] = False

            # Fill SEO fields fallback if needed
            if hasattr(instance, 'meta_title'):
                ret['meta_title'] = (
                    getattr(instance, 'meta_title', '') or
                    getattr(instance, 'title', '') or
                    getattr(instance, 'name', '') or ''
                )
            if hasattr(instance, 'meta_description'):
                ret['meta_description'] = (
                    getattr(instance, 'meta_description', '') or
                    getattr(instance, 'excerpt', '') or
                    getattr(instance, 'description', '') or ''
                )

            # Detail og_image
            img_val = getattr(instance, 'featuredImage', None) or getattr(instance, 'heroImage', None)
            if img_val:
                ret['og_image'] = make_absolute_url(img_val, request)

        # Convert image fields to absolute URLs
        for img_field in ('featuredImage', 'heroImage', 'avatar', 'coverImage', 'thumbnail', 'image', 'og_image'):
            if img_field in ret and ret[img_field]:
                ret[img_field] = make_absolute_url(ret[img_field], request)

        return ret


class CategorySerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    parent_slug = serializers.SlugRelatedField(source='parent', slug_field='slug', read_only=True)
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(parent__isnull=True),
        source='parent', required=False, allow_null=True,
    )

    class Meta:
        model = Category
        fields = ['id', 'slug', 'name', 'image', 'parent_id', 'parent_slug', 'layout_type', 'order', 'show_in_menu']


class CategoryChildSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'name', 'image', 'layout_type', 'order']


class CategoryMenuSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    """Top-level category with its visible sub-categories (used for header menu and category detail)."""
    children = serializers.SerializerMethodField()
    parent = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'slug', 'name', 'image', 'layout_type', 'order', 'parent', 'children']

    def get_children(self, obj):
        # Uses prefetched `visible_children` when available to avoid N+1 queries
        kids = getattr(obj, 'visible_children', None)
        if kids is None:
            kids = obj.children.filter(show_in_menu=True).order_by('order', 'id')
        return CategoryChildSerializer(kids, many=True, context=self.context).data

    def get_parent(self, obj):
        if not obj.parent_id:
            return None
        return CategoryChildSerializer(obj.parent, context=self.context).data


class AuthorSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'slug', 'name', 'bio', 'avatar', 'role', 'district']


class DistrictSliderImageSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DistrictSliderImage
        fields = ['id', 'image', 'caption', 'order']

    def get_image(self, obj):
        return make_absolute_url(obj.image, self.context.get('request'))


class DistrictSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    og_image = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = District
        fields = [
            'id', 'slug', 'name', 'description', 'meta_title', 'meta_description',
            'accentColor', 'heroImage', 'latitude', 'longitude', 'og_image',
        ]

    def get_og_image(self, obj):
        return make_absolute_url(obj.heroImage, self.context.get('request'))


class DistrictDetailSerializer(DistrictSerializer):
    slider_images = DistrictSliderImageSerializer(many=True, read_only=True)

    class Meta(DistrictSerializer.Meta):
        fields = DistrictSerializer.Meta.fields + ['slider_images']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class ArticleSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    district = DistrictSerializer(read_only=True)
    tags = serializers.SerializerMethodField(read_only=True)
    commentsCount = serializers.SerializerMethodField(read_only=True)
    og_image = serializers.SerializerMethodField(read_only=True)

    author_id = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(), source='author', write_only=True, required=False
    )
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True, required=False
    )
    district_id = serializers.PrimaryKeyRelatedField(
        queryset=District.objects.all(), source='district', write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'featuredImage', 'imageCaption',
            'meta_title', 'meta_description', 'og_image',
            'author', 'category', 'district', 'tags', 'status', 'publishedAt', 'updatedAt',
            'featured', 'breaking', 'popular', 'readTime', 'views', 'likes', 'commentsCount',
            'author_id', 'category_id', 'district_id'
        ]

    def to_internal_value(self, data):
        if isinstance(data, dict):
            # Normalize author, category, district ID writes
            if 'author' in data and not isinstance(data.get('author'), dict):
                data = data.copy()
                data['author_id'] = data.pop('author')
            if 'category' in data and not isinstance(data.get('category'), dict):
                data = data.copy()
                data['category_id'] = data.pop('category')
            if 'district' in data and not isinstance(data.get('district'), dict):
                data = data.copy()
                data['district_id'] = data.pop('district')
        return super().to_internal_value(data)

    def get_tags(self, obj):
        return [tag.name for tag in obj.tags_list.all()]

    def get_commentsCount(self, obj):
        return obj.comments.count()

    def get_og_image(self, obj):
        return make_absolute_url(obj.featuredImage, self.context.get('request'))


class ArticleCommentSerializer(serializers.ModelSerializer):
    replyCount = serializers.SerializerMethodField()

    class Meta:
        model = ArticleComment
        fields = '__all__'
        read_only_fields = ['user']
        extra_kwargs = {
            'article': {'required': False},
            'parent': {'required': False, 'allow_null': True}
        }

    def get_replyCount(self, obj):
        return obj.replies.count()

    def validate(self, attrs):
        if 'article' not in attrs:
            val = self.initial_data.get('article') or self.initial_data.get('articleId')
            if val:
                from .models import Article
                if str(val).isdigit():
                    article = Article.objects.filter(id=int(val)).first()
                else:
                    article = Article.objects.filter(slug=str(val)).first()
                if article:
                    attrs['article'] = article
                else:
                    raise serializers.ValidationError({'article': f'Article "{val}" not found.'})
            else:
                raise serializers.ValidationError({'article': 'Article is required.'})

        parent_val = self.initial_data.get('parent') or self.initial_data.get('parentId')
        if parent_val:
            from .models import ArticleComment
            parent_obj = ArticleComment.objects.filter(id=int(parent_val)).first()
            if parent_obj:
                attrs['parent'] = parent_obj

        return attrs


class VideoItemSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    district = DistrictSerializer(read_only=True)

    class Meta:
        model = VideoItem
        fields = ['id', 'title', 'thumbnail', 'duration', 'views', 'publishedAt', 'district', 'isShort']


class PhotoStorySerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    district = DistrictSerializer(read_only=True)

    class Meta:
        model = PhotoStory
        fields = ['id', 'title', 'description', 'coverImage', 'imageCount', 'photographer', 'publishedAt', 'district']


class BreakingNewsSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = BreakingNews
        fields = ['id', 'text', 'href', 'publishedAt']


class PartnerSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    district_slug = serializers.CharField(source='district.slug', read_only=True, allow_null=True)
    district_name = serializers.CharField(source='district.name', read_only=True, allow_null=True)

    class Meta:
        model = Partner
        fields = ['id', 'name', 'role', 'image', 'url', 'district', 'district_slug', 'district_name']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.image:
            image_name = str(instance.image.name) if instance.image else ""
            if image_name and (instance.image.storage.exists(image_name) or image_name.startswith('partners/')):
                ret['image'] = make_absolute_url(instance.image, self.context.get('request'))
            else:
                ret['image'] = image_name
        return ret


class HomePagePlacementSerializer(serializers.ModelSerializer):
    articles = ArticleSerializer(many=True, read_only=True)

    class Meta:
        model = HomePagePlacement
        fields = ['id', 'section_name', 'articles']


class DistrictThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DistrictTheme
        fields = '__all__'


class DistrictStatsSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = DistrictStats
        fields = '__all__'


class DistrictCultureSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = DistrictCulture
        fields = '__all__'


class DistrictPlaceSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = DistrictPlace
        fields = '__all__'


User = get_user_model()

class CustomUserCreateSerializer(BaseUserCreateSerializer):
    phone = serializers.CharField(max_length=20, required=True, write_only=True)
    username = serializers.CharField(max_length=150, required=False, allow_blank=True, default="")

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User._meta.pk.name,
            User.USERNAME_FIELD,
            'password',
            'phone',
            'first_name',
            'last_name',
            'email',
        )

    def validate_phone(self, value):
        cleaned = validate_phone_number(value)
        if UserProfile.objects.filter(phone=cleaned).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return cleaned

    def validate(self, attrs):
        phone = attrs.get('phone', '')
        username = attrs.get('username', '').strip()
        if not username:
            attrs['username'] = generate_username_from_phone(phone)

        # Copy attrs without 'phone' for password validation on User model
        user_attrs = {k: v for k, v in attrs.items() if k != 'phone'}
        user = User(**user_attrs)
        password = attrs.get("password")

        try:
            password_validation.validate_password(password, user)
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {"password": serializer_error[api_settings.NON_FIELD_ERRORS_KEY]}
            )

        return attrs

    def create(self, validated_data):
        phone = validated_data.pop('phone', None)
        user = super().create(validated_data)
        if phone:
            UserProfile.objects.update_or_create(user=user, defaults={'phone': phone})
        return user

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        profile = getattr(instance, 'profile', None)
        ret['phone'] = profile.phone if profile and profile.phone else ""
        return ret


class CustomUserSerializer(serializers.ModelSerializer):
    phone = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'phone')

    def get_phone(self, obj):
        profile = getattr(obj, 'profile', None)
        return profile.phone if profile and profile.phone else ""

# --- Hotel & Stay Serializers ---

class AmenitySerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ['id', 'name', 'icon']

class HotelRoomSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    image = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = HotelRoom
        fields = ['id', 'name', 'guests', 'bed_type', 'image', 'price']
        
    def get_image(self, obj):
        return make_absolute_url(obj.image, self.context.get('request'))

class HotelGallerySerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    image = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = HotelGallery
        fields = ['id', 'image', 'caption']
        
    def get_image(self, obj):
        return make_absolute_url(obj.image, self.context.get('request'))

class HotelNearbyPlaceSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = HotelNearbyPlace
        fields = ['id', 'name', 'distance']

class HotelSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    district = DistrictSerializer(read_only=True)
    hero_image = serializers.SerializerMethodField(read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    rooms = HotelRoomSerializer(many=True, read_only=True)
    gallery = HotelGallerySerializer(many=True, read_only=True)
    nearby_places = HotelNearbyPlaceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Hotel
        fields = [
            'id', 'slug', 'name', 'hotel_type', 'category', 'district',
            'address', 'municipality', 'latitude', 'longitude', 'rating', 'reviews_count',
            'hero_image', 'short_description', 'about', 'story',
            'quote_text', 'quote_author',
            'phone1', 'phone2', 'email', 'website', 'facebook_url', 'instagram_url',
            'amenities', 'highlights',
            'map_url', 'reach_bus', 'reach_airport', 'reach_highway',
            'rooms', 'gallery', 'nearby_places'
        ]
        
    def get_hero_image(self, obj):
        return make_absolute_url(obj.hero_image, self.context.get('request'))
