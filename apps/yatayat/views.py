from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter
from django.db.models import Q
from apps.common.permissions import IsAdminOrReadOnly
from .models import (
    TransportLocation, TransportService,
    TransportReport, EmergencyHelpline
)
from .serializers import (
    TransportLocationSerializer, TransportServiceSerializer,
    TransportReportSerializer, EmergencyHelplineSerializer
)

class TransportLocationViewSet(viewsets.ModelViewSet):
    queryset = TransportLocation.objects.select_related('district').all().order_by('-is_hub', 'name')
    serializer_class = TransportLocationSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ['name_en', 'name_ne', 'district__name_en', 'district__name_ne']

    def get_queryset(self):
        qs = super().get_queryset()
        is_hub = self.request.query_params.get('is_hub')
        if is_hub is not None:
            qs = qs.filter(is_hub=is_hub.lower() in ('true', '1'))
        district = self.request.query_params.get('district') or self.request.query_params.get('district__slug')
        if district:
            if str(district).isdigit():
                qs = qs.filter(district_id=int(district))
            else:
                qs = qs.filter(district__slug=district)
        return qs


class TransportServiceViewSet(viewsets.ModelViewSet):
    queryset = TransportService.objects.all().order_by('-verified', 'id')
    serializer_class = TransportServiceSerializer
    filter_backends = [SearchFilter]
    search_fields = [
        'title_en', 'title_ne', 'sub_title_en', 'sub_title_ne',
        'origin_name_en', 'origin_name_ne', 'destination_name_en', 'destination_name_ne',
        'contact_phone'
    ]

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
            # Default for public readers: approved and active
            qs = qs.filter(status='approved', is_active=True)

        service_type = self.request.query_params.get('type') or self.request.query_params.get('service_type')
        if service_type and service_type != 'all':
            qs = qs.filter(service_type=service_type)

        origin = self.request.query_params.get('origin')
        if origin:
            qs = qs.filter(Q(origin_name_en__icontains=origin) | Q(origin_name_ne__icontains=origin))

        destination = self.request.query_params.get('destination')
        if destination:
            qs = qs.filter(Q(destination_name_en__icontains=destination) | Q(destination_name_ne__icontains=destination))

        return qs

    def perform_create(self, serializer):
        is_staff = self.request.user and self.request.user.is_authenticated and self.request.user.is_staff
        status = 'approved' if is_staff else 'pending'
        verified = True if is_staff else False
        is_active = True if is_staff else False
        serializer.save(status=status, verified=verified, is_active=is_active)


class TransportReportViewSet(viewsets.ModelViewSet):
    queryset = TransportReport.objects.all().order_by('-created_at')
    serializer_class = TransportReportSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class EmergencyHelplineViewSet(viewsets.ModelViewSet):
    queryset = EmergencyHelpline.objects.select_related('district').all().order_by('order', 'id')
    serializer_class = EmergencyHelplineSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ['title_en', 'title_ne', 'phone_number']

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)
        district = self.request.query_params.get('district')
        if district:
            if str(district).isdigit():
                qs = qs.filter(district_id=int(district))
            else:
                qs = qs.filter(district__slug=district)
        return qs
