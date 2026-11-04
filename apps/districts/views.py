from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter
from apps.common.permissions import IsAdminOrReadOnly
from .models import (
    District, DistrictTheme, DistrictStats, DistrictCulture,
    DistrictPlace, Partner, PhotoSubmission, StorySubmission
)
from .serializers import (
    DistrictSerializer, DistrictDetailSerializer, DistrictThemeSerializer,
    DistrictStatsSerializer, DistrictCultureSerializer, DistrictPlaceSerializer,
    PartnerSerializer, PhotoSubmissionSerializer, StorySubmissionSerializer
)

class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.select_related('theme_data', 'stats_data', 'culture_data').prefetch_related('places', 'slider_images').all()
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DistrictDetailSerializer
        return DistrictSerializer


class DistrictThemeViewSet(viewsets.ModelViewSet):
    queryset = DistrictTheme.objects.all()
    serializer_class = DistrictThemeSerializer
    permission_classes = [IsAdminOrReadOnly]


class DistrictStatsViewSet(viewsets.ModelViewSet):
    queryset = DistrictStats.objects.all()
    serializer_class = DistrictStatsSerializer
    permission_classes = [IsAdminOrReadOnly]


class DistrictCultureViewSet(viewsets.ModelViewSet):
    queryset = DistrictCulture.objects.all()
    serializer_class = DistrictCultureSerializer
    permission_classes = [IsAdminOrReadOnly]


class DistrictPlaceViewSet(viewsets.ModelViewSet):
    queryset = DistrictPlace.objects.select_related('district').all()
    serializer_class = DistrictPlaceSerializer
    permission_classes = [IsAdminOrReadOnly]


class PartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.select_related('district').all()
    serializer_class = PartnerSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ['name_en', 'name_ne', 'role_en', 'role_ne']

    def get_queryset(self):
        qs = super().get_queryset()
        district_param = self.request.query_params.get('district') or self.request.query_params.get('district__slug')
        if district_param:
            if str(district_param).isdigit():
                qs = qs.filter(district_id=int(district_param))
            else:
                qs = qs.filter(district__slug=district_param)
        return qs


class PhotoSubmissionViewSet(viewsets.ModelViewSet):
    queryset = PhotoSubmission.objects.all().order_by('-created_at')
    serializer_class = PhotoSubmissionSerializer

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get_queryset(self):
        qs = super().get_queryset()
        status_param = self.request.query_params.get('status')
        if status_param:
            if status_param == 'all' and (self.request.user and self.request.user.is_authenticated and self.request.user.is_staff):
                pass
            elif status_param in ['pending', 'rejected']:
                if self.request.user and self.request.user.is_authenticated and self.request.user.is_staff:
                    qs = qs.filter(status=status_param)
                else:
                    qs = qs.none()
            else:
                qs = qs.filter(status=status_param)
        else:
            qs = qs.filter(status='approved')

        district = self.request.query_params.get('district') or self.request.query_params.get('district__slug')
        if district:
            if str(district).isdigit():
                qs = qs.filter(district_id=int(district))
            else:
                qs = qs.filter(district__slug=district)
        return qs

    def perform_create(self, serializer):
        serializer.save(status='pending')


class StorySubmissionViewSet(viewsets.ModelViewSet):
    queryset = StorySubmission.objects.all().order_by('-created_at')
    serializer_class = StorySubmissionSerializer

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get_queryset(self):
        qs = super().get_queryset()
        status_param = self.request.query_params.get('status')
        if status_param:
            if status_param == 'all' and (self.request.user and self.request.user.is_authenticated and self.request.user.is_staff):
                pass
            elif status_param in ['pending', 'rejected']:
                if self.request.user and self.request.user.is_authenticated and self.request.user.is_staff:
                    qs = qs.filter(status=status_param)
                else:
                    qs = qs.none()
            else:
                qs = qs.filter(status=status_param)
        else:
            qs = qs.filter(status='approved')

        district = self.request.query_params.get('district') or self.request.query_params.get('district__slug')
        if district:
            if str(district).isdigit():
                qs = qs.filter(district_id=int(district))
            else:
                qs = qs.filter(district__slug=district)

        category = self.request.query_params.get('category') or self.request.query_params.get('main_category')
        if category and category != 'all':
            qs = qs.filter(main_category=category)

        return qs

    def perform_create(self, serializer):
        serializer.save(status='pending')

