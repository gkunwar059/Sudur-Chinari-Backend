from datetime import timedelta
from django.utils import timezone
from django.db.models import F, Q, Case, When, Value, IntegerField
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from apps.common.permissions import IsAdminOrReadOnly
from .models import PopupAd, BannerAd
from .serializers import (
    PopupAdSerializer,
    BannerAdSerializer,
    BannerAdRequestSerializer
)

class PopupAdViewSet(viewsets.ModelViewSet):
    queryset = PopupAd.objects.all()
    serializer_class = PopupAdSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def active(self, request):
        active_ad = PopupAd.objects.filter(is_active=True).first()
        if not active_ad:
            return Response({"active": False, "data": None})
        serializer = self.get_serializer(active_ad, context={'request': request})
        return Response({"active": True, "data": serializer.data})


class BannerAdViewSet(viewsets.ModelViewSet):
    queryset = BannerAd.objects.all()
    serializer_class = BannerAdSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        qs = BannerAd.objects.all()

        # Non-staff users can only list approved & active ads
        if not (user and user.is_authenticated and user.is_staff):
            today = timezone.now().date()
            qs = qs.filter(
                is_active=True,
                status='approved'
            ).filter(
                Q(start_date__isnull=True) | Q(start_date__lte=today),
                Q(end_date__isnull=True) | Q(end_date__gte=today)
            )

        # Query filters
        placement = self.request.query_params.get('placement')
        if placement:
            qs = qs.filter(placement=placement)

        page = self.request.query_params.get('page')
        if page and page != 'all':
            qs = qs.filter(Q(page=page) | Q(page='all'))

        status_param = self.request.query_params.get('status')
        if status_param and user and user.is_authenticated and user.is_staff:
            qs = qs.filter(status=status_param)

        return qs

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def active(self, request):
        today = timezone.now().date()
        qs = BannerAd.objects.filter(
            is_active=True,
            status='approved'
        ).filter(
            Q(start_date__isnull=True) | Q(start_date__lte=today),
            Q(end_date__isnull=True) | Q(end_date__gte=today)
        )

        placement = request.query_params.get('placement')
        if placement:
            qs = qs.filter(placement=placement)

        page = request.query_params.get('page')
        if page and page != 'all':
            # Priority to ads targeting the exact page, then 'all', then by priority & recency
            qs = qs.filter(Q(page=page) | Q(page='all')).annotate(
                page_match=Case(
                    When(page=page, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField()
                )
            ).order_by('-page_match', '-priority', '-created_at')
        else:
            qs = qs.order_by('-priority', '-created_at')

        ad = qs.first()
        if not ad:
            return Response({"active": False, "data": None})

        serializer = self.get_serializer(ad, context={'request': request})
        return Response({"active": True, "data": serializer.data})

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def request_ad(self, request):
        """
        Allows an authenticated user to submit an ad request / creative.
        The ad is saved with status='pending' and is_active=False until verified by admin.
        """
        serializer = BannerAdRequestSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        duration_days = data.pop('duration_days', 30) or 30

        today = timezone.now().date()
        start_date = data.get('start_date') or today
        end_date = data.get('end_date') or (start_date + timedelta(days=duration_days))

        # Autofill contact info from user if missing
        contact_name = data.get('contact_name')
        if not contact_name:
            contact_name = (
                f"{request.user.first_name} {request.user.last_name}".strip()
                or request.user.username
                or request.user.email
            )

        contact_email = data.get('contact_email') or request.user.email or ""

        # Admin users can automatically approve if requested
        is_staff = request.user.is_staff
        requested_status = 'approved' if is_staff and request.data.get('auto_approve') == 'true' else 'pending'
        is_active = True if requested_status == 'approved' else False

        data['requested_by'] = request.user
        data['status'] = requested_status
        data['is_active'] = is_active
        data['start_date'] = start_date
        data['end_date'] = end_date
        data['contact_name'] = contact_name
        data['contact_email'] = contact_email

        ad = BannerAd.objects.create(**data)

        out_serializer = BannerAdSerializer(ad, context={'request': request})
        message = (
            "तपाईंको विज्ञापन प्रमाणीकरणका लागि सफलतापूर्वक पेश गरियो। प्रशासकले प्रमाणीकरण गरेपछि यो प्रकाशित हुनेछ।"
            if requested_status == 'pending'
            else "विज्ञापन सफलतापूर्वक प्रकाशित गरियो।"
        )
        return Response({
            "success": True,
            "message": message,
            "data": out_serializer.data
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_ads(self, request):
        """
        Returns list of ads submitted by the current authenticated user.
        """
        qs = BannerAd.objects.filter(requested_by=request.user).order_by('-created_at')
        serializer = self.get_serializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        ad = self.get_object()
        ad.status = 'approved'
        ad.is_active = True
        ad.rejection_reason = ""
        ad.save(update_fields=['status', 'is_active', 'rejection_reason', 'updated_at'])
        serializer = self.get_serializer(ad, context={'request': request})
        return Response({
            "success": True,
            "message": "Advertisement approved successfully.",
            "data": serializer.data
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        ad = self.get_object()
        ad.status = 'rejected'
        ad.is_active = False
        reason = request.data.get('reason', '')
        if reason:
            ad.rejection_reason = reason
        ad.save(update_fields=['status', 'is_active', 'rejection_reason', 'updated_at'])
        serializer = self.get_serializer(ad, context={'request': request})
        return Response({
            "success": True,
            "message": "Advertisement marked as rejected.",
            "data": serializer.data
        })

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def click(self, request, pk=None):
        ad = self.get_object()
        ad.clicks_count = F('clicks_count') + 1
        ad.save(update_fields=['clicks_count'])
        ad.refresh_from_db()
        return Response({'clicks': ad.clicks_count})

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def impression(self, request, pk=None):
        ad = self.get_object()
        ad.impressions_count = F('impressions_count') + 1
        ad.save(update_fields=['impressions_count'])
        ad.refresh_from_db()
        return Response({'impressions': ad.impressions_count})

