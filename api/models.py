"""
Backward compatibility layer for models.
Models are now defined in dedicated domain apps:
- apps.accounts (UserProfile)
- apps.districts (District, DistrictSliderImage, DistrictTheme, DistrictStats, DistrictCulture, DistrictPlace, Partner)
- apps.articles (Category, Author, Article, Tag, ArticleComment, BreakingNews, HomePagePlacement)
- apps.hotels (Amenity, Hotel, HotelRoom, HotelGallery, HotelNearbyPlace)
- apps.multimedia (VideoItem, PhotoStory)
- apps.ads (PopupAd)
"""

from apps.accounts.models import UserProfile
from apps.districts.models import (
    District, DistrictSliderImage, DistrictTheme, DistrictStats,
    DistrictCulture, DistrictPlace, Partner
)
from apps.articles.models import (
    Category, Author, Article, Tag, ArticleComment,
    BreakingNews, HomePagePlacement
)
from apps.hotels.models import (
    Amenity, Hotel, HotelRoom, HotelGallery, HotelNearbyPlace
)
from apps.multimedia.models import VideoItem, PhotoStory
from apps.ads.models import PopupAd

__all__ = [
    'UserProfile',
    'District', 'DistrictSliderImage', 'DistrictTheme', 'DistrictStats',
    'DistrictCulture', 'DistrictPlace', 'Partner',
    'Category', 'Author', 'Article', 'Tag', 'ArticleComment',
    'BreakingNews', 'HomePagePlacement',
    'Amenity', 'Hotel', 'HotelRoom', 'HotelGallery', 'HotelNearbyPlace',
    'VideoItem', 'PhotoStory',
    'PopupAd',
]
