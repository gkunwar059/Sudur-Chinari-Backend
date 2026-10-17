from rest_framework import viewsets
from rest_framework.filters import SearchFilter
from django.db.models import Q
from apps.common.permissions import IsAdminOrReadOnly
from .models import Hotel
from .serializers import HotelSerializer

class HotelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only public ViewSet for Hotels, Resorts and Homestays.
    Supports filtering by district, category, and text search.
    """
    queryset = Hotel.objects.select_related('district', 'category').prefetch_related(
        'amenities', 'rooms', 'gallery', 'nearby_places'
    ).all()
    serializer_class = HotelSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [SearchFilter]
    search_fields = ['name_en', 'name_ne', 'address_en', 'address_ne', 'municipality_en', 'municipality_ne', 'about_en', 'about_ne']

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_val = self.kwargs.get(lookup_url_kwarg)
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
                qs = qs.filter(Q(category__slug=category) | Q(category__parent__slug=category))
                
        hotel_type = self.request.query_params.get('hotel_type')
        if hotel_type:
            qs = qs.filter(hotel_type__iexact=hotel_type)
            
        return qs
