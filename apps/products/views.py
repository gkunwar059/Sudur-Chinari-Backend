from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django.db.models import Q
from apps.common.permissions import IsAdminOrReadOnly
from .models import ProductCategory, LocalProduct, ProductProducer
from .serializers import (
    ProductCategorySerializer, LocalProductSerializer, ProductProducerSerializer
)

class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.filter(is_active=True).order_by('order', 'id')
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'


class LocalProductViewSet(viewsets.ModelViewSet):
    queryset = LocalProduct.objects.select_related('category', 'district').prefetch_related('producers').all()
    serializer_class = LocalProductSerializer
    lookup_field = 'slug'
    filter_backends = [SearchFilter]
    search_fields = ['name_en', 'name_ne', 'description_en', 'description_ne', 'district__name_en', 'district__name_ne', 'farmer_name']

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve', 'by_district']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get_object(self):
        lookup_val = self.kwargs.get(self.lookup_url_kwarg or self.lookup_field)
        if lookup_val:
            if str(lookup_val).isdigit():
                obj = self.get_queryset().filter(id=int(lookup_val)).first()
                if obj:
                    return obj
            obj = self.get_queryset().filter(slug__iexact=lookup_val).first()
            if obj:
                return obj
        return super().get_object()

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

        category = self.request.query_params.get('category') or self.request.query_params.get('category__slug')
        if category:
            if str(category).isdigit():
                qs = qs.filter(category_id=int(category))
            else:
                qs = qs.filter(category__slug=category)

        featured = self.request.query_params.get('featured')
        if featured is not None:
            qs = qs.filter(is_featured=featured.lower() in ('true', '1'))

        return qs

    def perform_create(self, serializer):
        is_staff = self.request.user and self.request.user.is_authenticated and self.request.user.is_staff
        status = 'approved' if is_staff else 'pending'
        is_verified = True if is_staff else False
        serializer.save(status=status, is_verified=is_verified)

    @action(detail=False, methods=['get'], url_path='by-district/(?P<district_slug>[^/.]+)')
    def by_district(self, request, district_slug=None):
        if str(district_slug).isdigit():
            qs = self.get_queryset().filter(district_id=int(district_slug))
        else:
            qs = self.get_queryset().filter(district__slug=district_slug)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class ProductProducerViewSet(viewsets.ModelViewSet):
    queryset = ProductProducer.objects.select_related('district').prefetch_related('products').all()
    serializer_class = ProductProducerSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ['name_en', 'name_ne', 'phone', 'municipality_address_en', 'municipality_address_ne']

    def get_queryset(self):
        qs = super().get_queryset()
        district = self.request.query_params.get('district') or self.request.query_params.get('district__slug')
        if district:
            if str(district).isdigit():
                qs = qs.filter(district_id=int(district))
            else:
                qs = qs.filter(district__slug=district)

        product = self.request.query_params.get('product') or self.request.query_params.get('product__slug')
        if product:
            if str(product).isdigit():
                qs = qs.filter(products__id=int(product))
            else:
                qs = qs.filter(products__slug=product)

        return qs
