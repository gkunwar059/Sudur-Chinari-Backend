from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.filters import SearchFilter
from django.db.models import F
from apps.common.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from .models import VideoItem, VideoComment, PhotoStory, PhotoStoryImage, VideoLike, VideoCommentLike
from .serializers import (
    VideoItemSerializer, VideoCommentSerializer,
    PhotoStorySerializer, PhotoStoryImageSerializer
)

class VideoItemViewSet(viewsets.ModelViewSet):
    queryset = VideoItem.objects.select_related('district').prefetch_related('comments').all()
    serializer_class = VideoItemSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ['title_en', 'title_ne', 'district__name_en', 'district__name_ne']

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsAdminOrReadOnly()]

    def get_queryset(self):
        qs = super().get_queryset()
        is_short = self.request.query_params.get('isShort') or self.request.query_params.get('is_short')
        if is_short is not None:
            qs = qs.filter(isShort=is_short.lower() in ('true', '1'))

        district = self.request.query_params.get('district') or self.request.query_params.get('district__slug')
        if district:
            if str(district).isdigit():
                qs = qs.filter(district_id=int(district))
            else:
                qs = qs.filter(district__slug=district)
        return qs

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        video = self.get_object()
        user = request.user
        like_obj = VideoLike.objects.filter(video=video, user=user).first()
        if like_obj:
            like_obj.delete()
            count = VideoLike.objects.filter(video=video).count()
            if video.likes > count:
                video.likes = max(0, video.likes - 1)
            else:
                video.likes = count
            video.save(update_fields=['likes'])
            return Response({'likes': video.likes, 'has_liked': False})
        else:
            VideoLike.objects.get_or_create(video=video, user=user)
            count = VideoLike.objects.filter(video=video).count()
            if video.likes < count:
                video.likes = count
            else:
                video.likes = video.likes + 1
            video.save(update_fields=['likes'])
            return Response({'likes': video.likes, 'has_liked': True})

    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def like_status(self, request, pk=None):
        video = self.get_object()
        user = request.user
        has_liked = False
        if user and user.is_authenticated:
            has_liked = VideoLike.objects.filter(video=video, user=user).exists()
        return Response({'likes': video.likes, 'has_liked': has_liked})

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def view(self, request, pk=None):
        video = self.get_object()
        video.views = F('views') + 1
        video.save(update_fields=['views'])
        video.refresh_from_db()
        return Response({'views': video.views})


class VideoCommentViewSet(viewsets.ModelViewSet):
    queryset = VideoComment.objects.all().order_by('-createdAt')
    serializer_class = VideoCommentSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        user = self.request.user
        name = (user.get_full_name() or '').strip()
        if not name:
            name = getattr(user, 'name', '') or user.username or user.email or 'प्रमाणित प्रयोगकर्ता'
        serializer.save(user=user, authorName=name)

    def get_queryset(self):
        qs = super().get_queryset()
        video_param = self.request.query_params.get('videoId') or self.request.query_params.get('video')
        if video_param:
            if str(video_param).isdigit():
                qs = qs.filter(video_id=int(video_param))
        return qs

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        comment = self.get_object()
        user = request.user
        like_obj = VideoCommentLike.objects.filter(comment=comment, user=user).first()
        if like_obj:
            like_obj.delete()
            count = VideoCommentLike.objects.filter(comment=comment).count()
            if comment.likes > count:
                comment.likes = max(0, comment.likes - 1)
            else:
                comment.likes = count
            comment.save(update_fields=['likes'])
            return Response({'likes': comment.likes, 'has_liked': False})
        else:
            VideoCommentLike.objects.get_or_create(comment=comment, user=user)
            count = VideoCommentLike.objects.filter(comment=comment).count()
            if comment.likes < count:
                comment.likes = count
            else:
                comment.likes = comment.likes + 1
            comment.save(update_fields=['likes'])
            return Response({'likes': comment.likes, 'has_liked': True})


class PhotoStoryViewSet(viewsets.ModelViewSet):
    queryset = PhotoStory.objects.select_related('district').prefetch_related('images').all()
    serializer_class = PhotoStorySerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ['title_en', 'title_ne', 'description_en', 'description_ne', 'photographer']

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsAdminOrReadOnly()]

    def get_queryset(self):
        qs = super().get_queryset()
        district = self.request.query_params.get('district') or self.request.query_params.get('district__slug')
        if district:
            if str(district).isdigit():
                qs = qs.filter(district_id=int(district))
            else:
                qs = qs.filter(district__slug=district)
        return qs
