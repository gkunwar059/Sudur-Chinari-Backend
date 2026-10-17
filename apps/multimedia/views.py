from rest_framework import viewsets
from apps.common.permissions import IsAdminOrReadOnly
from .models import VideoItem, PhotoStory
from .serializers import VideoItemSerializer, PhotoStorySerializer

class VideoItemViewSet(viewsets.ModelViewSet):
    queryset = VideoItem.objects.select_related('district').all()
    serializer_class = VideoItemSerializer
    permission_classes = [IsAdminOrReadOnly]


class PhotoStoryViewSet(viewsets.ModelViewSet):
    queryset = PhotoStory.objects.select_related('district').all()
    serializer_class = PhotoStorySerializer
    permission_classes = [IsAdminOrReadOnly]
