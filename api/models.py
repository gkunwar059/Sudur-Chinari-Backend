from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User

class Category(models.Model):
    """
    News category that also drives the dynamic header menu.
    Top-level categories (parent=None) appear in the main nav bar;
    their children appear as a sub-menu strip (with images) under it.
    Only two levels are supported (parent -> child).
    """
    LAYOUT_CHOICES = (
        ('base', 'Base Layout'),
        ('news', 'News Layout'),
        ('sports', 'Sports Layout'),
        ('stayor_hotel', 'Stay or Hotel Layout'),
        ('tourism', 'Tourism Layout'),
        ('politics', 'Politics Layout'),
    )
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=255, default="")
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        limit_choices_to={'parent__isnull': True},
        help_text="Leave empty for a top-level menu item. Set to make this a sub-category.",
    )
    layout_type = models.CharField(
        max_length=20,
        choices=LAYOUT_CHOICES,
        default='base',
        help_text="Choose the frontend UI layout for this category."
    )
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first in the menu.")
    show_in_menu = models.BooleanField(default=True, help_text="Show this category in the header menu.")

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['order', 'id']

    def __str__(self):
        label = self.name or self.slug
        if self.parent_id:
            return f"{self.parent} → {label}"
        return label

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.parent_id:
            if self.pk and self.parent_id == self.pk:
                raise ValidationError({'parent': "A category cannot be its own parent."})
            if self.parent and self.parent.parent_id:
                raise ValidationError({'parent': "Only two menu levels are supported. Choose a top-level category."})
            if self.pk and self.children.exists():
                raise ValidationError({'parent': "This category has sub-categories, so it must stay top-level."})

    def save(self, *args, **kwargs):
        # Always inherit layout_type from parent
        if self.parent:
            self.layout_type = self.parent.layout_type
            
        super().save(*args, **kwargs)
        
        # Cascade layout_type to all children
        if not self.parent:
            self.children.update(layout_type=self.layout_type)

class Author(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=255, default="")
    bio = models.TextField(blank=True, default="")
    avatar = models.URLField(max_length=500, blank=True, null=True)
    role = models.CharField(max_length=255)
    district = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Author"
        verbose_name_plural = "Authors"

    def __str__(self):
        return self.name or self.slug

class District(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=255, default="")
    description = models.TextField(blank=True, default="")
    meta_title = models.CharField(max_length=255, blank=True, default="")
    meta_description = models.TextField(blank=True, default="")
    accentColor = models.CharField(max_length=50, blank=True, null=True)
    heroImage = models.ImageField(upload_to="districts/", blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True, default=None)
    longitude = models.FloatField(blank=True, null=True, default=None)

    class Meta:
        verbose_name = "District"
        verbose_name_plural = "Districts"

    def __str__(self):
        return self.name or self.slug

class DistrictSliderImage(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='slider_images')
    image = models.ImageField(upload_to="districts/slider/")
    caption = models.CharField(max_length=255, blank=True, default="")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "District Slider Image"
        verbose_name_plural = "District Slider Images"

    def __str__(self):
        return f"{self.district.name or self.district.slug} Slider #{self.id}"

class Article(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('review', 'Review'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )
    
    title = models.CharField(max_length=500, default="")
    slug = models.SlugField(unique=True, max_length=255)
    excerpt = models.TextField(default="")
    content = models.TextField(default="")
    featuredImage = models.URLField(max_length=500, blank=True, null=True)
    imageCaption = models.CharField(max_length=255, blank=True, default="")
    meta_title = models.CharField(max_length=255, blank=True, default="")
    meta_description = models.TextField(blank=True, default="")
    
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='articles')
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='articles',
        limit_choices_to=~Q(layout_type__in=['stayor_hotel', 'stay'])
    )
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    publishedAt = models.DateTimeField(null=True, blank=True)
    updatedAt = models.DateTimeField(auto_now=True)
    
    featured = models.BooleanField(default=False)
    breaking = models.BooleanField(default=False)
    popular = models.BooleanField(default=False)
    
    readTime = models.IntegerField(default=5)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def __str__(self):
        return self.title or self.slug

class Tag(models.Model):
    name = models.CharField(max_length=100)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='tags_list')

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return self.name

class ArticleComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    authorName = models.CharField(max_length=255)
    authorLocation = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Article Comment"
        verbose_name_plural = "Article Comments"

    def __str__(self):
        return f"Comment by {self.authorName} on {self.article_id}"

class VideoItem(models.Model):
    title = models.CharField(max_length=255, default="")
    thumbnail = models.URLField(max_length=500)
    duration = models.CharField(max_length=20)
    views = models.IntegerField(default=0)
    publishedAt = models.DateTimeField()
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    isShort = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Video"
        verbose_name_plural = "Videos"

    def __str__(self):
        return self.title

class PhotoStory(models.Model):
    title = models.CharField(max_length=255, default="")
    description = models.TextField(default="")
    coverImage = models.URLField(max_length=500)
    imageCount = models.IntegerField(default=0)
    photographer = models.CharField(max_length=255)
    publishedAt = models.DateTimeField()
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Photo Story"
        verbose_name_plural = "Photo Stories"

    def __str__(self):
        return self.title

class BreakingNews(models.Model):
    text = models.CharField(max_length=500, default="")
    href = models.URLField(max_length=500)
    publishedAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Breaking News"
        verbose_name_plural = "Breaking News"

    def __str__(self):
        return self.text

class Partner(models.Model):
    name = models.CharField(max_length=255, default="")
    role = models.CharField(max_length=255, default="")
    image = models.ImageField(upload_to="partners/", blank=True, null=True, verbose_name="Logo / Image")
    url = models.URLField(max_length=500, blank=True, null=True)
    district = models.ForeignKey(
        District,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="partners",
        verbose_name="District",
        help_text="Select a district for district-specific partner, or leave blank to show on the main page."
    )

    class Meta:
        verbose_name = "Partner"
        verbose_name_plural = "Partners"

    def __str__(self):
        if self.district:
            return f"{self.name} ({self.district.name})"
        return self.name

class HomePagePlacement(models.Model):
    section_name = models.CharField(max_length=100, unique=True)
    articles = models.ManyToManyField(Article, related_name='placements')

    class Meta:
        verbose_name = "Homepage Placement"
        verbose_name_plural = "Homepage Placements"

    def __str__(self):
        return self.section_name

class DistrictTheme(models.Model):
    district = models.OneToOneField(District, on_delete=models.CASCADE, related_name='theme_data')
    primary = models.CharField(max_length=50)
    dark = models.CharField(max_length=50)
    light = models.CharField(max_length=50)
    border = models.CharField(max_length=50)
    badgeBg = models.CharField(max_length=50)
    badgeText = models.CharField(max_length=50)
    gradient = models.CharField(max_length=255)

    class Meta:
        verbose_name = "District Theme"
        verbose_name_plural = "District Themes"

    def __str__(self):
        return f"Theme for {self.district}"

class DistrictStats(models.Model):
    district = models.OneToOneField(District, on_delete=models.CASCADE, related_name='stats_data')
    area = models.CharField(max_length=100)
    population = models.CharField(max_length=100)
    headquarters = models.CharField(max_length=100, default="")
    elevation = models.CharField(max_length=100)
    palikas_total = models.IntegerField(default=0)
    palikas_municipalities = models.IntegerField(default=0)
    palikas_rural = models.IntegerField(default=0)
    majorRivers = models.CharField(max_length=255, default="")
    literacy = models.CharField(max_length=100)

    class Meta:
        verbose_name = "District Statistics"
        verbose_name_plural = "District Statistics"

    def __str__(self):
        return f"Stats for {self.district}"

class DistrictCulture(models.Model):
    district = models.OneToOneField(District, on_delete=models.CASCADE, related_name='culture_data')
    folkDance = models.TextField(default="")
    festivals = models.TextField(default="")
    cuisine = models.TextField(default="")
    dialects = models.TextField(default="")

    class Meta:
        verbose_name = "District Culture"
        verbose_name_plural = "District Cultures"

    def __str__(self):
        return f"Culture for {self.district}"

class DistrictPlace(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='places')
    title = models.CharField(max_length=255, default="")
    description = models.TextField(default="")
    category = models.CharField(max_length=100)
    image = models.URLField(max_length=500, blank=True, null=True)
    highlight = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "District Place"
        verbose_name_plural = "District Places"

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, unique=True, null=True, blank=False, verbose_name="Phone Number")

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.username} ({self.phone or 'No phone'})"

# --- Hotel & Stay Models ---

class Amenity(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, help_text="Lucide icon name (e.g., 'Wifi')")
    
    class Meta:
        verbose_name_plural = "Amenities"
        
    def __str__(self):
        return self.name

class Hotel(models.Model):
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='hotels',
        limit_choices_to={'layout_type__in': ['stayor_hotel', 'stay']}
    )
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    slug = models.SlugField(unique=True)
    
    name = models.CharField(max_length=255)
    hotel_type = models.CharField(max_length=100, default="Hotel")
    
    address = models.CharField(max_length=255)
    municipality = models.CharField(max_length=255, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=0.0)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=0.0)
    
    rating = models.FloatField(default=0.0)
    reviews_count = models.IntegerField(default=0)
    
    hero_image = models.ImageField(upload_to="hotels/hero/")
    
    short_description = models.CharField(max_length=500, blank=True)
    about = models.TextField()
    story = models.TextField(blank=True)
    quote_text = models.TextField(blank=True)
    quote_author = models.CharField(max_length=100, blank=True)
    
    # Contact
    phone1 = models.CharField(max_length=20)
    phone2 = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    
    # Features
    amenities = models.ManyToManyField(Amenity, blank=True)
    highlights = models.JSONField(default=list, help_text="List of string highlights")
    
    # Reach
    map_url = models.URLField(blank=True)
    reach_bus = models.CharField(max_length=100, blank=True)
    reach_airport = models.CharField(max_length=100, blank=True)
    reach_highway = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return self.name

class HotelRoom(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    name = models.CharField(max_length=100)
    guests = models.IntegerField(default=2)
    bed_type = models.CharField(max_length=100)
    image = models.ImageField(upload_to="hotels/rooms/", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

class HotelGallery(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to="hotels/gallery/")
    caption = models.CharField(max_length=255, blank=True)

class HotelNearbyPlace(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='nearby_places')
    name = models.CharField(max_length=255)
    distance = models.CharField(max_length=50) # e.g. 2.5 km
