from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.articles.views import (
    CategoryViewSet, AuthorViewSet, ArticleViewSet,
    ArticleCommentViewSet, BreakingNewsViewSet,
    HomePagePlacementViewSet, SitemapView
)
from apps.districts.views import (
    DistrictViewSet, DistrictThemeViewSet, DistrictStatsViewSet,
    DistrictCultureViewSet, DistrictPlaceViewSet, PartnerViewSet
)
from apps.hotels.views import HotelViewSet
from apps.multimedia.views import VideoItemViewSet, PhotoStoryViewSet
from apps.ads.views import PopupAdViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'authors', AuthorViewSet)
router.register(r'districts', DistrictViewSet)
router.register(r'articles', ArticleViewSet)
router.register(r'comments', ArticleCommentViewSet)
router.register(r'videos', VideoItemViewSet)
router.register(r'photo-stories', PhotoStoryViewSet)
router.register(r'breaking-news', BreakingNewsViewSet)
router.register(r'partners', PartnerViewSet)
router.register(r'homepage-placements', HomePagePlacementViewSet)
router.register(r'district-themes', DistrictThemeViewSet)
router.register(r'district-stats', DistrictStatsViewSet)
router.register(r'district-cultures', DistrictCultureViewSet)
router.register(r'district-places', DistrictPlaceViewSet)
router.register(r'hotels', HotelViewSet, basename='hotel')
router.register(r'popup-ads', PopupAdViewSet, basename='popup-ad')

urlpatterns = [
    path('sitemap/', SitemapView.as_view(), name='api-sitemap'),
    path('', include(router.urls)),
]
