from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter
from django.db.models import Q, F, Prefetch
from django.utils import timezone
from apps.common.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from apps.districts.models import District
from .models import (
    Category, Author, Article, Tag, ArticleComment,
    BreakingNews, HomePagePlacement
)
from .serializers import (
    CategorySerializer, CategoryMenuSerializer, AuthorSerializer,
    ArticleSerializer, ArticleCommentSerializer, BreakingNewsSerializer,
    HomePagePlacementSerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            layout_type = self.request.query_params.get('layout_type')
            if layout_type:
                qs = qs.filter(layout_type=layout_type)
        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CategoryMenuSerializer
        return CategorySerializer

    @action(detail=False, methods=['get'])
    def menu(self, request):
        visible_children = Prefetch(
            'children',
            queryset=Category.objects.filter(show_in_menu=True).order_by('order', 'id'),
            to_attr='visible_children'
        )
        roots = (
            Category.objects
            .filter(parent__isnull=True, show_in_menu=True)
            .prefetch_related(visible_children)
            .order_by('order', 'id')
        )
        serializer = CategoryMenuSerializer(roots, many=True, context={'request': request})
        return Response(serializer.data)


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.select_related('author', 'category', 'district').prefetch_related('tags_list', 'comments')
    serializer_class = ArticleSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_val = self.kwargs.get(lookup_url_kwarg)
        if lookup_val:
            if str(lookup_val).isdigit():
                obj = self.get_queryset().filter(id=int(lookup_val)).first()
                if obj:
                    self.check_object_permissions(self.request, obj)
                    return obj
            obj = self.get_queryset().filter(slug__iexact=lookup_val).first()
            if obj:
                self.check_object_permissions(self.request, obj)
                return obj
        return super().get_object()

    def get_queryset(self):
        qs = super().get_queryset()
        status = self.request.query_params.get('status')
        if status:
            qs = qs.filter(status=status)
            
        category = self.request.query_params.get('category') or self.request.query_params.get('category__slug')
        if category:
            qs = qs.filter(Q(category__slug=category) | Q(category__parent__slug=category))

        district = self.request.query_params.get('district') or self.request.query_params.get('district__slug')
        if district:
            if str(district).isdigit():
                qs = qs.filter(district_id=int(district))
            else:
                qs = qs.filter(district__slug=district)

        author = self.request.query_params.get('author') or self.request.query_params.get('author__slug')
        if author:
            if str(author).isdigit():
                qs = qs.filter(author_id=int(author))
            else:
                qs = qs.filter(author__slug=author)

        featured = self.request.query_params.get('featured')
        if featured is not None:
            qs = qs.filter(featured=featured.lower() in ('true', '1'))

        breaking = self.request.query_params.get('breaking')
        if breaking is not None:
            qs = qs.filter(breaking=breaking.lower() in ('true', '1'))

        popular = self.request.query_params.get('popular')
        if popular is not None:
            qs = qs.filter(popular=popular.lower() in ('true', '1'))
            
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(title_en__icontains=search) | 
                Q(title_ne__icontains=search) | 
                Q(excerpt_en__icontains=search) |
                Q(excerpt_ne__icontains=search) |
                Q(content_en__icontains=search) |
                Q(content_ne__icontains=search)
            )

        ordering = self.request.query_params.get('ordering')
        if ordering:
            ordering_fields = [f.strip() for f in ordering.split(',')]
            mapped_ordering = []
            for field in ordering_fields:
                if field in ('created_at', 'createdAt'):
                    mapped_ordering.append('publishedAt')
                elif field in ('-created_at', '-createdAt'):
                    mapped_ordering.append('-publishedAt')
                else:
                    mapped_ordering.append(field)
            try:
                qs = qs.order_by(*mapped_ordering)
            except Exception:
                pass
            
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


class BreakingNewsViewSet(viewsets.ModelViewSet):
    queryset = BreakingNews.objects.all()
    serializer_class = BreakingNewsSerializer
    permission_classes = [IsAdminOrReadOnly]


class HomePagePlacementViewSet(viewsets.ModelViewSet):
    queryset = HomePagePlacement.objects.prefetch_related('articles').all()
    serializer_class = HomePagePlacementSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'section_name'


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
