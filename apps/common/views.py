from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django.db.models import Q, F
from apps.common.permissions import IsAdminOrReadOnly
from .models import TrendingTopic, ContactInquiry, NewsletterSubscriber
from .serializers import (
    TrendingTopicSerializer, ContactInquirySerializer, NewsletterSubscriberSerializer
)
from apps.articles.models import Article
from apps.districts.models import District
from apps.hotels.models import Hotel
from apps.multimedia.models import VideoItem, PhotoStory
from apps.products.models import LocalProduct
from apps.yatayat.models import TransportService

class TrendingTopicViewSet(viewsets.ModelViewSet):
    queryset = TrendingTopic.objects.filter(is_active=True).order_by('order', '-search_count')
    serializer_class = TrendingTopicSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'


class ContactInquiryViewSet(viewsets.ModelViewSet):
    queryset = ContactInquiry.objects.all().order_by('-created_at')
    serializer_class = ContactInquirySerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class NewsletterSubscriberViewSet(viewsets.ModelViewSet):
    queryset = NewsletterSubscriber.objects.all().order_by('-created_at')
    serializer_class = NewsletterSubscriberSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def create(self, request, *args, **kwargs):
        email = (request.data.get('email') or '').strip().lower()
        if not email:
            return Response({'email': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST)
        obj, created = NewsletterSubscriber.objects.get_or_create(email=email, defaults={'is_active': True})
        serializer = self.get_serializer(obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class GlobalSearchView(APIView):
    """
    Unified global search endpoint across articles, districts, hotels, videos,
    photo stories, local products, and transport routes.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({
                "query": "",
                "total_count": 0,
                "articles": [],
                "districts": [],
                "hotels": [],
                "videos": [],
                "photos": [],
                "products": [],
                "yatayat": [],
            })

        # Track trending search atomically
        try:
            topic = TrendingTopic.objects.filter(
                Q(name_en__iexact=query) | Q(name_ne__iexact=query) | Q(slug__iexact=query)
            ).first()
            if topic:
                TrendingTopic.objects.filter(id=topic.id).update(search_count=F('search_count') + 1)
        except Exception:
            pass

        # 1. Articles (only published articles)
        article_matches = Article.objects.filter(
            Q(status='published'),
            Q(title_en__icontains=query) | Q(title_ne__icontains=query) |
            Q(excerpt_en__icontains=query) | Q(excerpt_ne__icontains=query)
        ).select_related('category', 'district', 'author')[:12]

        from apps.articles.serializers import ArticleSerializer
        articles_data = ArticleSerializer(article_matches, many=True, context={'request': request}).data

        # 2. Districts
        district_matches = District.objects.filter(
            Q(name_en__icontains=query) | Q(name_ne__icontains=query) |
            Q(description_en__icontains=query) | Q(description_ne__icontains=query)
        )[:6]
        from apps.districts.serializers import DistrictSerializer
        districts_data = DistrictSerializer(district_matches, many=True, context={'request': request}).data

        # 3. Hotels
        hotel_matches = Hotel.objects.filter(
            Q(name_en__icontains=query) | Q(name_ne__icontains=query) |
            Q(address_en__icontains=query) | Q(address_ne__icontains=query) |
            Q(municipality_en__icontains=query) | Q(municipality_ne__icontains=query)
        ).select_related('district', 'category')[:6]
        from apps.hotels.serializers import HotelSerializer
        hotels_data = HotelSerializer(hotel_matches, many=True, context={'request': request}).data

        # 4. Videos
        video_matches = VideoItem.objects.filter(
            Q(title_en__icontains=query) | Q(title_ne__icontains=query)
        ).select_related('district')[:6]
        from apps.multimedia.serializers import VideoItemSerializer
        videos_data = VideoItemSerializer(video_matches, many=True, context={'request': request}).data

        # 5. Photos
        photo_matches = PhotoStory.objects.filter(
            Q(title_en__icontains=query) | Q(title_ne__icontains=query) |
            Q(description_en__icontains=query) | Q(description_ne__icontains=query)
        ).select_related('district')[:6]
        from apps.multimedia.serializers import PhotoStorySerializer
        photos_data = PhotoStorySerializer(photo_matches, many=True, context={'request': request}).data

        # 6. Products (only approved products)
        product_matches = LocalProduct.objects.filter(
            Q(status='approved'),
            Q(name_en__icontains=query) | Q(name_ne__icontains=query) |
            Q(description_en__icontains=query) | Q(description_ne__icontains=query)
        ).select_related('category', 'district')[:6]
        from apps.products.serializers import LocalProductSerializer
        products_data = LocalProductSerializer(product_matches, many=True, context={'request': request}).data

        # 7. Transport / Yatayat (only approved & active transport services)
        yatayat_matches = TransportService.objects.filter(
            Q(status='approved', is_active=True),
            Q(title_en__icontains=query) | Q(title_ne__icontains=query) |
            Q(origin_name_en__icontains=query) | Q(origin_name_ne__icontains=query) |
            Q(destination_name_en__icontains=query) | Q(destination_name_ne__icontains=query)
        )[:6]
        from apps.yatayat.serializers import TransportServiceSerializer
        yatayat_data = TransportServiceSerializer(yatayat_matches, many=True, context={'request': request}).data

        total_count = (
            len(articles_data) + len(districts_data) + len(hotels_data) +
            len(videos_data) + len(photos_data) + len(products_data) + len(yatayat_data)
        )

        return Response({
            "query": query,
            "total_count": total_count,
            "articles": articles_data,
            "districts": districts_data,
            "hotels": hotels_data,
            "videos": videos_data,
            "photos": photos_data,
            "products": products_data,
            "yatayat": yatayat_data,
        })
