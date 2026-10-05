from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django.utils import timezone
from django.db.models import F, Q, Prefetch
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from .models import (
    Category, Author, District, Article, ArticleComment, VideoItem, PhotoStory, BreakingNews,
    Partner, HomePagePlacement, DistrictTheme, DistrictStats, DistrictCulture, DistrictPlace,
    Hotel
)
from .serializers import (
    CategorySerializer, CategoryMenuSerializer, AuthorSerializer, DistrictSerializer, DistrictDetailSerializer, ArticleSerializer,
    ArticleCommentSerializer, VideoItemSerializer, PhotoStorySerializer, BreakingNewsSerializer,
    PartnerSerializer, HomePagePlacementSerializer, DistrictThemeSerializer, DistrictStatsSerializer,
    DistrictCultureSerializer, DistrictPlaceSerializer, HotelSerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.select_related('parent').all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'

    @staticmethod
    def _visible_children_prefetch():
        return Prefetch(
            'children',
            queryset=Category.objects.filter(show_in_menu=True).order_by('order', 'id'),
            to_attr='visible_children',
        )

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'retrieve':
            return qs.prefetch_related(self._visible_children_prefetch())
        parent = self.request.query_params.get('parent')
        if parent:
            if parent.lower() in ('null', 'none', 'root'):
                qs = qs.filter(parent__isnull=True)
            else:
                qs = qs.filter(parent__slug=parent)
        return qs

    def get_serializer_class(self):
        if self.action in ('retrieve', 'menu'):
            return CategoryMenuSerializer
        return CategorySerializer

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def menu(self, request):
        """Header menu: visible top-level categories with their visible sub-categories."""
        qs = (
            Category.objects.filter(parent__isnull=True, show_in_menu=True)
            .order_by('order', 'id')
            .prefetch_related(self._visible_children_prefetch())
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'

class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all().prefetch_related('places')
    serializer_class = DistrictSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DistrictDetailSerializer
        return DistrictSerializer

    def get_queryset(self):
        qs = District.objects.all().prefetch_related('places')
        if self.action == 'retrieve':
            qs = qs.prefetch_related('slider_images')
        return qs

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.select_related('author', 'category', 'district').prefetch_related('tags_list', 'comments')
    serializer_class = ArticleSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get('status')
        if status:
            qs = qs.filter(status=status)
        category = self.request.query_params.get('category')
        if category:
            # Parent category pages include articles from all of their sub-categories
            qs = qs.filter(Q(category__slug=category) | Q(category__parent__slug=category))
            
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(title_en__icontains=search) | 
                Q(title_ne__icontains=search) | 
                Q(excerpt_en__icontains=search) |
                Q(excerpt_ne__icontains=search)
            )
            
        return qs

class ArticleCommentViewSet(viewsets.ModelViewSet):
    queryset = ArticleComment.objects.all().order_by('-createdAt')
    serializer_class = ArticleCommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    def perform_create(self, serializer):
        user = self.request.user if (self.request.user and self.request.user.is_authenticated) else None
        serializer.save(user=user)

    def get_queryset(self):
        qs = super().get_queryset()
        article_param = self.request.query_params.get('articleId') or self.request.query_params.get('article')
        if article_param:
            if str(article_param).isdigit():
                qs = qs.filter(article_id=int(article_param))
            else:
                qs = qs.filter(article__slug=article_param)
        return qs

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def like(self, request, pk=None):
        comment = self.get_object()
        comment.likes = F('likes') + 1
        comment.save(update_fields=['likes'])
        comment.refresh_from_db()
        return Response({'likes': comment.likes})

class VideoItemViewSet(viewsets.ModelViewSet):
    queryset = VideoItem.objects.select_related('district').all()
    serializer_class = VideoItemSerializer
    permission_classes = [IsAdminOrReadOnly]

class PhotoStoryViewSet(viewsets.ModelViewSet):
    queryset = PhotoStory.objects.select_related('district').all()
    serializer_class = PhotoStorySerializer
    permission_classes = [IsAdminOrReadOnly]

class BreakingNewsViewSet(viewsets.ModelViewSet):
    queryset = BreakingNews.objects.all()
    serializer_class = BreakingNewsSerializer
    permission_classes = [IsAdminOrReadOnly]

class PartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.select_related('district').all()
    serializer_class = PartnerSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        district_param = self.request.query_params.get('district')
        main_param = self.request.query_params.get('main')

        if main_param and main_param.lower() in ['true', '1']:
            return qs.filter(district__isnull=True)

        if district_param:
            if district_param.lower() in ['null', 'none', 'main']:
                return qs.filter(district__isnull=True)
            if district_param.isdigit():
                return qs.filter(district_id=int(district_param))
            return qs.filter(district__slug=district_param)

        return qs

class HomePagePlacementViewSet(viewsets.ModelViewSet):
    queryset = HomePagePlacement.objects.prefetch_related(
        'articles__author', 'articles__category', 'articles__district', 'articles__tags_list'
    ).all()
    serializer_class = HomePagePlacementSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'section_name'

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
    permission_classes = [IsAuthenticatedOrReadOnly]


class SitemapView(APIView):
    """
    Returns every public object that has its own page:
    Articles (published), Districts, and Categories.
    Shape: [{ "type": str, "slug": str, "updated_at": str, "has_ne": bool }]
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        sitemap_data = []

        # 1. Published articles
        articles = Article.objects.filter(status='published').only('slug', 'updatedAt', 'title_ne', 'content_ne')
        for a in articles:
            has_ne = bool(a.title_ne and a.title_ne.strip())
            updated_at = a.updatedAt.isoformat() if a.updatedAt else timezone.now().isoformat()
            sitemap_data.append({
                "type": "article",
                "slug": a.slug,
                "updated_at": updated_at,
                "has_ne": has_ne
            })

        # 2. Districts
        districts = District.objects.all().only('slug', 'name_ne')
        now_iso = timezone.now().isoformat()
        for d in districts:
            has_ne = bool(d.name_ne and d.name_ne.strip())
            sitemap_data.append({
                "type": "district",
                "slug": d.slug,
                "updated_at": now_iso,
                "has_ne": has_ne
            })

        # 3. Categories
        categories = Category.objects.all().only('slug', 'name_ne')
        for c in categories:
            has_ne = bool(c.name_ne and c.name_ne.strip())
            sitemap_data.append({
                "type": "category",
                "slug": c.slug,
                "updated_at": now_iso,
                "has_ne": has_ne
            })

        return Response(sitemap_data)

class HotelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing Hotels/Stays.
    """
    queryset = Hotel.objects.prefetch_related('amenities', 'rooms', 'gallery', 'nearby_places').select_related('category', 'district').all()
    serializer_class = HotelSerializer
    lookup_field = 'slug'
    lookup_field = 'slug'

    def get_queryset(self):
        qs = Hotel.objects.prefetch_related('amenities', 'rooms', 'gallery', 'nearby_places').select_related('category', 'district').all()
        
        category = self.request.query_params.get('category__slug')
        if category:
            qs = qs.filter(category__slug=category)
            
        district = self.request.query_params.get('district__slug')
        if district:
            qs = qs.filter(district__slug=district)
            
        hotel_type = self.request.query_params.get('hotel_type')
        if hotel_type:
            qs = qs.filter(hotel_type=hotel_type)
            
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(name_en__icontains=search) | 
                Q(name_ne__icontains=search) | 
                Q(slug__icontains=search)
            )
            
        return qs
