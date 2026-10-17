from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from apps.common.permissions import IsAdminOrReadOnly
from .models import (
    District, DistrictTheme, DistrictStats, DistrictCulture,
    DistrictPlace, Partner
)
from .serializers import (
    DistrictSerializer, DistrictDetailSerializer, DistrictThemeSerializer,
    DistrictStatsSerializer, DistrictCultureSerializer, DistrictPlaceSerializer,
    PartnerSerializer
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
