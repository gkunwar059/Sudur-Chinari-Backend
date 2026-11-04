from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.articles.views import (
    CategoryViewSet, AuthorViewSet, ArticleViewSet,
    ArticleCommentViewSet, BreakingNewsViewSet,
    HomePagePlacementViewSet, SitemapView, ArticleBookmarkViewSet,
    HeroSlideViewSet
)
from apps.districts.views import (
    DistrictViewSet, DistrictThemeViewSet, DistrictStatsViewSet,
    DistrictCultureViewSet, DistrictPlaceViewSet, PartnerViewSet,
    PhotoSubmissionViewSet, StorySubmissionViewSet
)
from apps.hotels.views import HotelViewSet
from apps.multimedia.views import VideoItemViewSet, PhotoStoryViewSet, VideoCommentViewSet
from apps.ads.views import PopupAdViewSet, BannerAdViewSet
from apps.products.views import (
    ProductCategoryViewSet, LocalProductViewSet, ProductProducerViewSet
)
from apps.yatayat.views import (
    TransportServiceViewSet, TransportLocationViewSet,
    TransportReportViewSet, EmergencyHelplineViewSet
)
from apps.common.views import (
    TrendingTopicViewSet, ContactInquiryViewSet,
    NewsletterSubscriberViewSet, GlobalSearchView
)

router = DefaultRouter()

# Articles & Taxonomy
router.register(r'categories', CategoryViewSet)
router.register(r'authors', AuthorViewSet)
router.register(r'articles', ArticleViewSet)
router.register(r'comments', ArticleCommentViewSet)
router.register(r'bookmarks', ArticleBookmarkViewSet, basename='article-bookmark')
router.register(r'breaking-news', BreakingNewsViewSet)
router.register(r'homepage-placements', HomePagePlacementViewSet)
router.register(r'hero-slides', HeroSlideViewSet, basename='hero-slide')

# Districts & Submissions
router.register(r'districts', DistrictViewSet)
router.register(r'district-themes', DistrictThemeViewSet)
router.register(r'district-stats', DistrictStatsViewSet)
router.register(r'district-cultures', DistrictCultureViewSet)
router.register(r'district-places', DistrictPlaceViewSet)
router.register(r'partners', PartnerViewSet)
router.register(r'photo-contributions', PhotoSubmissionViewSet, basename='photo-contribution')
router.register(r'story-contributions', StorySubmissionViewSet, basename='story-contribution')

# Hospitality
router.register(r'hotels', HotelViewSet, basename='hotel')

# Multimedia
router.register(r'videos', VideoItemViewSet)
router.register(r'video-comments', VideoCommentViewSet, basename='video-comment')
router.register(r'photo-stories', PhotoStoryViewSet)

# Advertising
router.register(r'popup-ads', PopupAdViewSet, basename='popup-ad')
router.register(r'banner-ads', BannerAdViewSet, basename='banner-ad')

# Local Products & Agriculture
router.register(r'product-categories', ProductCategoryViewSet, basename='product-category')
router.register(r'products', LocalProductViewSet, basename='local-product')
router.register(r'producers', ProductProducerViewSet, basename='product-producer')
router.register(r'farmers', ProductProducerViewSet, basename='farmer')

# Transport / Yatayat
router.register(r'yatayat', TransportServiceViewSet, basename='yatayat-service')
router.register(r'yatayat-services', TransportServiceViewSet, basename='yatayat-services')
router.register(r'transport-services', TransportServiceViewSet, basename='transport-service')
router.register(r'yatayat-locations', TransportLocationViewSet, basename='yatayat-location')
router.register(r'transport-locations', TransportLocationViewSet, basename='transport-location')
router.register(r'yatayat-registrations', TransportServiceViewSet, basename='yatayat-registration')
router.register(r'yatayat-reports', TransportReportViewSet, basename='yatayat-report')
router.register(r'yatayat-helplines', EmergencyHelplineViewSet, basename='yatayat-helpline')
router.register(r'emergency-helplines', EmergencyHelplineViewSet, basename='emergency-helpline')

# Common / Discovery
router.register(r'trending-topics', TrendingTopicViewSet, basename='trending-topic')
router.register(r'contact-inquiries', ContactInquiryViewSet, basename='contact-inquiry')
router.register(r'newsletter', NewsletterSubscriberViewSet, basename='newsletter-subscriber')

urlpatterns = [
    path('sitemap/', SitemapView.as_view(), name='api-sitemap'),
    path('search/', GlobalSearchView.as_view(), name='api-global-search'),
    path('', include(router.urls)),
]
