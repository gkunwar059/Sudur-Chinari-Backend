"""
Backward compatibility layer for views and viewsets.
Viewsets are now located in their respective domain apps:
- apps.articles.views (CategoryViewSet, AuthorViewSet, ArticleViewSet, ArticleCommentViewSet, BreakingNewsViewSet, HomePagePlacementViewSet, SitemapView)
- apps.districts.views (DistrictViewSet, DistrictThemeViewSet, DistrictStatsViewSet, DistrictCultureViewSet, DistrictPlaceViewSet, PartnerViewSet)
- apps.hotels.views (HotelViewSet)
- apps.multimedia.views (VideoItemViewSet, PhotoStoryViewSet)
- apps.ads.views (PopupAdViewSet)
"""

from apps.articles.views import (
    CategoryViewSet,
    AuthorViewSet,
    ArticleViewSet,
    ArticleCommentViewSet,
    BreakingNewsViewSet,
    HomePagePlacementViewSet,
    SitemapView,
)
from apps.districts.views import (
    DistrictViewSet,
    DistrictThemeViewSet,
    DistrictStatsViewSet,
    DistrictCultureViewSet,
    DistrictPlaceViewSet,
    PartnerViewSet,
)
from apps.hotels.views import (
    HotelViewSet,
)
from apps.multimedia.views import (
    VideoItemViewSet,
    PhotoStoryViewSet,
)
from apps.ads.views import (
    PopupAdViewSet,
)

__all__ = [
    'CategoryViewSet',
    'AuthorViewSet',
    'ArticleViewSet',
    'ArticleCommentViewSet',
    'BreakingNewsViewSet',
    'HomePagePlacementViewSet',
    'SitemapView',
    'DistrictViewSet',
    'DistrictThemeViewSet',
    'DistrictStatsViewSet',
    'DistrictCultureViewSet',
    'DistrictPlaceViewSet',
    'PartnerViewSet',
    'HotelViewSet',
    'VideoItemViewSet',
    'PhotoStoryViewSet',
    'PopupAdViewSet',
]
