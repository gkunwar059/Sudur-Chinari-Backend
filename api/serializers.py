"""
Backward compatibility layer for serializers.
Serializers are now located in their respective domain apps:
- apps.common.serializers_base (TranslatedAdminSerializerMixin, make_absolute_url, get_bilingual_or_localized)
- apps.accounts.serializers (CustomUserCreateSerializer, CustomUserSerializer)
- apps.districts.serializers (DistrictThemeSerializer, DistrictStatsSerializer, DistrictCultureSerializer, DistrictPlaceSerializer, DistrictSliderImageSerializer, DistrictSerializer, DistrictDetailSerializer, PartnerSerializer)
- apps.articles.serializers (CategorySerializer, CategoryChildSerializer, CategoryMenuSerializer, AuthorSerializer, TagSerializer, ArticleSerializer, ArticleCommentSerializer, BreakingNewsSerializer, HomePagePlacementSerializer)
- apps.hotels.serializers (AmenitySerializer, HotelRoomSerializer, HotelGallerySerializer, HotelNearbyPlaceSerializer, HotelSerializer)
- apps.multimedia.serializers (VideoItemSerializer, PhotoStorySerializer)
- apps.ads.serializers (PopupAdSerializer)
"""

from apps.common.serializers_base import (
    TranslatedAdminSerializerMixin,
    make_absolute_url,
    get_bilingual_or_localized,
)
from apps.accounts.serializers import (
    CustomUserCreateSerializer,
    CustomUserSerializer,
)
from apps.districts.serializers import (
    DistrictThemeSerializer,
    DistrictStatsSerializer,
    DistrictCultureSerializer,
    DistrictPlaceSerializer,
    DistrictSliderImageSerializer,
    DistrictSerializer,
    DistrictDetailSerializer,
    PartnerSerializer,
)
from apps.articles.serializers import (
    CategorySerializer,
    CategoryChildSerializer,
    CategoryMenuSerializer,
    AuthorSerializer,
    TagSerializer,
    ArticleSerializer,
    ArticleCommentSerializer,
    BreakingNewsSerializer,
    HomePagePlacementSerializer,
)
from apps.hotels.serializers import (
    AmenitySerializer,
    HotelRoomSerializer,
    HotelGallerySerializer,
    HotelNearbyPlaceSerializer,
    HotelSerializer,
)
from apps.multimedia.serializers import (
    VideoItemSerializer,
    PhotoStorySerializer,
)
from apps.ads.serializers import (
    PopupAdSerializer,
)

__all__ = [
    'TranslatedAdminSerializerMixin',
    'make_absolute_url',
    'get_bilingual_or_localized',
    'CustomUserCreateSerializer',
    'CustomUserSerializer',
    'DistrictThemeSerializer',
    'DistrictStatsSerializer',
    'DistrictCultureSerializer',
    'DistrictPlaceSerializer',
    'DistrictSliderImageSerializer',
    'DistrictSerializer',
    'DistrictDetailSerializer',
    'PartnerSerializer',
    'CategorySerializer',
    'CategoryChildSerializer',
    'CategoryMenuSerializer',
    'AuthorSerializer',
    'TagSerializer',
    'ArticleSerializer',
    'ArticleCommentSerializer',
    'BreakingNewsSerializer',
    'HomePagePlacementSerializer',
    'AmenitySerializer',
    'HotelRoomSerializer',
    'HotelGallerySerializer',
    'HotelNearbyPlaceSerializer',
    'HotelSerializer',
    'VideoItemSerializer',
    'PhotoStorySerializer',
    'PopupAdSerializer',
]
