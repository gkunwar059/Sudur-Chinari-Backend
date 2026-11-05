from rest_framework import serializers
from apps.common.serializers_base import TranslatedAdminSerializerMixin, make_absolute_url
from apps.districts.serializers import DistrictSerializer
from .models import VideoItem, VideoComment, PhotoStory, PhotoStoryImage, VideoLike, VideoCommentLike

class VideoCommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()
    authorName = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model = VideoComment
        fields = [
            'id', 'video', 'parent', 'authorName', 'authorLocation',
            'content', 'createdAt', 'likes', 'has_liked', 'replies'
        ]
        read_only_fields = ['likes', 'createdAt']

    def to_internal_value(self, data):
        if hasattr(data, 'dict'):
            mapped = data.dict()
        else:
            mapped = dict(data)

        if 'user_name' in mapped and not mapped.get('authorName'):
            mapped['authorName'] = mapped['user_name']

        request = self.context.get('request')
        if request and getattr(request, 'user', None) and request.user.is_authenticated:
            user = request.user
            name = (user.get_full_name() or '').strip()
            if not name:
                name = getattr(user, 'name', '') or user.username or user.email or 'प्रमाणित प्रयोगकर्ता'
            if not mapped.get('authorName'):
                mapped['authorName'] = name

        return super().to_internal_value(mapped)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['user_name'] = instance.authorName
        ret['created_at'] = instance.createdAt
        return ret

    def get_has_liked(self, obj):
        request = self.context.get('request')
        if request and getattr(request, 'user', None) and request.user.is_authenticated:
            return VideoCommentLike.objects.filter(comment=obj, user=request.user).exists()
        return False

    def get_replies(self, obj):
        if obj.parent_id is not None:
            return []
        replies = obj.replies.all().order_by('createdAt')
        return VideoCommentSerializer(replies, many=True, context=self.context).data


import re

class HybridThumbnailField(serializers.Field):
    """Accepts both multipart file uploads and string URLs / relative media paths."""
    def to_internal_value(self, data):
        if not data:
            return None
        if hasattr(data, 'read') or hasattr(data, 'chunks'):
            return data
        if isinstance(data, str):
            return data.strip()
        return data

    def to_representation(self, value):
        if not value:
            return None
        if hasattr(value, 'url'):
            return value.url
        return str(value)


class VideoItemSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    district = DistrictSerializer(read_only=True)
    district_id = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    comments_count = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()

    title = serializers.CharField(required=False, allow_blank=True, default="")
    title_en = serializers.CharField(required=False, allow_blank=True)
    title_ne = serializers.CharField(required=False, allow_blank=True)
    thumbnail = HybridThumbnailField(required=False, allow_null=True)
    duration = serializers.CharField(required=False, allow_blank=True, default="3:00")
    publishedAt = serializers.DateTimeField(required=False)
    youtube_id = serializers.CharField(required=False, allow_blank=True, default="")
    video_url = serializers.CharField(required=False, allow_blank=True, default="")
    isShort = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = VideoItem
        fields = [
            'id', 'title', 'thumbnail', 'video_url', 'youtube_id',
            'duration', 'views', 'likes', 'has_liked', 'publishedAt', 'district', 'district_id', 'isShort',
            'comments_count', 'title_en', 'title_ne'
        ]

    def get_has_liked(self, obj):
        request = self.context.get('request')
        if request and getattr(request, 'user', None) and request.user.is_authenticated:
            return VideoLike.objects.filter(video=obj, user=request.user).exists()
        return False

    def get_comments_count(self, obj):
        return obj.comments.count()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.thumbnail:
            ret['thumbnail'] = make_absolute_url(instance.thumbnail, self.context.get('request'))
        return ret

    def to_internal_value(self, data):
        if hasattr(data, 'dict'):
            mapped = data.dict()
        else:
            mapped = dict(data)

        # Preserve translation fields
        title_en = mapped.get('title_en') or mapped.get('title') or ''
        title_ne = mapped.get('title_ne') or ''

        district_val = mapped.get('district') or mapped.get('district_id')
        if district_val:
            mapped['district_id'] = str(district_val)

        if not mapped.get('title'):
            mapped['title'] = title_en or title_ne or 'Video Report'

        if not mapped.get('publishedAt'):
            mapped['publishedAt'] = timezone.now().isoformat()

        if not mapped.get('duration'):
            mapped['duration'] = '3:00'

        # Auto-extract youtube_id if full URL was provided
        yt_input = str(mapped.get('youtube_id') or mapped.get('video_url') or '')
        if 'youtube.com' in yt_input or 'youtu.be' in yt_input:
            if '/shorts/' in yt_input:
                mapped['isShort'] = True
                m = re.search(r'/shorts/([a-zA-Z0-9_-]{11})', yt_input)
                if m:
                    mapped['youtube_id'] = m.group(1)
            elif 'youtu.be/' in yt_input:
                m = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', yt_input)
                if m:
                    mapped['youtube_id'] = m.group(1)
            elif 'v=' in yt_input:
                m = re.search(r'v=([a-zA-Z0-9_-]{11})', yt_input)
                if m:
                    mapped['youtube_id'] = m.group(1)

        # Auto-generate thumbnail if missing and youtube_id exists
        yt_id = mapped.get('youtube_id')
        if not mapped.get('thumbnail'):
            if yt_id:
                mapped['thumbnail'] = f"https://img.youtube.com/vi/{yt_id}/hqdefault.jpg"
            else:
                mapped['thumbnail'] = "https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?w=800"

        ret = super().to_internal_value(mapped)

        if title_en:
            ret['title_en'] = title_en
        if title_ne:
            ret['title_ne'] = title_ne
        if district_val:
            ret['district_raw'] = district_val

        return ret

    def create(self, validated_data):
        district_raw = validated_data.pop('district_raw', None)
        district_id_val = validated_data.pop('district_id', None)
        district_val = validated_data.pop('district', None)
        district_identifier = district_raw or district_id_val or district_val
        district_obj = None
        if district_identifier:
            if isinstance(district_identifier, District):
                district_obj = district_identifier
            elif str(district_identifier).isdigit():
                district_obj = District.objects.filter(id=int(district_identifier)).first()
            else:
                district_obj = District.objects.filter(slug=district_identifier).first()

        if not validated_data.get('publishedAt'):
            validated_data['publishedAt'] = timezone.now()

        video = VideoItem.objects.create(district=district_obj, **validated_data)
        return video


class PhotoStoryImageSerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = PhotoStoryImage
        fields = ['id', 'image', 'caption', 'order', 'created_at']

    def get_image(self, obj):
        if obj.image:
            return make_absolute_url(obj.image, self.context.get('request'))
        return obj.image_url or ""


from django.utils import timezone
from apps.districts.models import District

class PhotoStorySerializer(TranslatedAdminSerializerMixin, serializers.ModelSerializer):
    district = DistrictSerializer(read_only=True)
    district_id = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    images = PhotoStoryImageSerializer(many=True, read_only=True)
    imageCount = serializers.SerializerMethodField()
    coverImage = serializers.CharField(required=False, allow_blank=True, default="")
    publishedAt = serializers.DateTimeField(required=False)
    photographer = serializers.CharField(required=False, allow_blank=True)

    title = serializers.CharField(required=False, allow_blank=True, default="")
    description = serializers.CharField(required=False, allow_blank=True, default="")
    title_en = serializers.CharField(required=False, allow_blank=True)
    title_ne = serializers.CharField(required=False, allow_blank=True)
    description_en = serializers.CharField(required=False, allow_blank=True)
    description_ne = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = PhotoStory
        fields = [
            'id', 'title', 'description', 'coverImage', 'imageCount',
            'photographer', 'publishedAt', 'district', 'district_id', 'images',
            'title_en', 'title_ne', 'description_en', 'description_ne'
        ]

    def get_imageCount(self, obj):
        actual_count = obj.images.count()
        return actual_count if actual_count > 0 else (obj.imageCount or 1)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.coverImage:
            ret['coverImage'] = make_absolute_url(instance.coverImage, self.context.get('request'))
        return ret

    def to_internal_value(self, data):
        if hasattr(data, 'dict'):
            mapped = data.dict()
        else:
            mapped = dict(data)

        # Preserve translation fields
        title_en = mapped.get('title_en') or mapped.get('title') or ''
        title_ne = mapped.get('title_ne') or ''
        desc_en = mapped.get('description_en') or mapped.get('description') or ''
        desc_ne = mapped.get('description_ne') or ''

        district_val = mapped.get('district') or mapped.get('district_id')
        if district_val:
            mapped['district_id'] = str(district_val)

        if not mapped.get('title'):
            mapped['title'] = title_en or title_ne or 'Photo Story'
        if not mapped.get('description'):
            mapped['description'] = desc_en or desc_ne or ''

        if not mapped.get('photographer'):
            request = self.context.get('request')
            user_name = ''
            if request and getattr(request, 'user', None) and request.user.is_authenticated:
                user_name = request.user.get_full_name() or request.user.username or ''
            mapped['photographer'] = user_name or 'Contributor'

        if not mapped.get('publishedAt'):
            mapped['publishedAt'] = timezone.now().isoformat()

        if not mapped.get('coverImage'):
            mapped['coverImage'] = ''

        ret = super().to_internal_value(mapped)

        if title_en:
            ret['title_en'] = title_en
        if title_ne:
            ret['title_ne'] = title_ne
        if desc_en:
            ret['description_en'] = desc_en
        if desc_ne:
            ret['description_ne'] = desc_ne
        if district_val:
            ret['district_raw'] = district_val

        return ret

    def create(self, validated_data):
        district_raw = validated_data.pop('district_raw', None)
        district_id_val = validated_data.pop('district_id', None)
        district_val = validated_data.pop('district', None)
        district_identifier = district_raw or district_id_val or district_val
        district_obj = None
        if district_identifier:
            if isinstance(district_identifier, District):
                district_obj = district_identifier
            elif str(district_identifier).isdigit():
                district_obj = District.objects.filter(id=int(district_identifier)).first()
            else:
                district_obj = District.objects.filter(slug=district_identifier).first()

        request = self.context.get('request')
        if not validated_data.get('photographer') and request and request.user and request.user.is_authenticated:
            validated_data['photographer'] = request.user.get_full_name() or request.user.username

        if not validated_data.get('publishedAt'):
            validated_data['publishedAt'] = timezone.now()

        story = PhotoStory.objects.create(district=district_obj, **validated_data)

        if request:
            import json
            req_data = getattr(request, 'data', None) or getattr(request, 'POST', {})
            req_files = getattr(request, 'FILES', None) or {}

            gallery_meta = []
            gallery_meta_raw = req_data.get('gallery_meta') or req_data.get('images_meta')
            if gallery_meta_raw:
                try:
                    if isinstance(gallery_meta_raw, str):
                        gallery_meta = json.loads(gallery_meta_raw)
                    elif isinstance(gallery_meta_raw, list):
                        gallery_meta = gallery_meta_raw
                except Exception:
                    gallery_meta = []

            # Extract uploaded files
            uploaded_files = req_files.getlist('images') if hasattr(req_files, 'getlist') else []
            if not uploaded_files and hasattr(req_files, 'getlist'):
                uploaded_files = req_files.getlist('gallery_images')

            if not uploaded_files:
                idx = 0
                while f'image_{idx}' in req_files:
                    uploaded_files.append(req_files[f'image_{idx}'])
                    idx += 1

            if not uploaded_files and 'image' in req_files:
                uploaded_files = [req_files['image']]

            image_urls = req_data.getlist('image_urls') if hasattr(req_data, 'getlist') else []
            if not image_urls and req_data.get('image_url'):
                image_urls = [req_data.get('image_url')]

            created_images = []
            for idx, file_obj in enumerate(uploaded_files):
                meta = gallery_meta[idx] if idx < len(gallery_meta) and isinstance(gallery_meta[idx], dict) else {}
                cap_en = meta.get('caption_en') or req_data.get(f'caption_{idx}_en') or req_data.get('caption_en') or ''
                cap_ne = meta.get('caption_ne') or req_data.get(f'caption_{idx}_ne') or req_data.get('caption_ne') or ''
                order = meta.get('order', idx + 1)

                psi = PhotoStoryImage.objects.create(
                    story=story,
                    image=file_obj,
                    caption=cap_en or cap_ne or '',
                    caption_en=cap_en,
                    caption_ne=cap_ne,
                    order=order
                )
                created_images.append(psi)

            for idx, url in enumerate(image_urls, start=len(created_images)):
                meta = gallery_meta[idx] if idx < len(gallery_meta) and isinstance(gallery_meta[idx], dict) else {}
                cap_en = meta.get('caption_en') or ''
                cap_ne = meta.get('caption_ne') or ''
                order = meta.get('order', idx + 1)
                psi = PhotoStoryImage.objects.create(
                    story=story,
                    image_url=url,
                    caption=cap_en or cap_ne or '',
                    caption_en=cap_en,
                    caption_ne=cap_ne,
                    order=order
                )
                created_images.append(psi)

            if created_images:
                story.imageCount = len(created_images)
                if not story.coverImage:
                    first_img = created_images[0]
                    if first_img.image:
                        story.coverImage = first_img.image.url
                    elif first_img.image_url:
                        story.coverImage = first_img.image_url
                story.save(update_fields=['imageCount', 'coverImage'])

        return story
