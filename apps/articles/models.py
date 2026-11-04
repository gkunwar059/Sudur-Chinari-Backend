from django.db import models
from django.db.models import Q
from django.contrib.auth import get_user_model

User = get_user_model()

LAYOUT_CHOICES = [
    ('default', 'Default (General Category Layout)'),
    ('news', 'News Layout'),
    ('politics', 'Politics Layout'),
    ('sports', 'Sports Layout'),
    ('tourism', 'Tourism Layout'),
    ('stay', 'Stay Layout'),
]

SYSTEM_SLUGS = {
    'news', 'stay', 'politics', 'sports', 'tourism',
    'society', 'economy', 'education', 'health', 'culture',
    'opinion', 'agriculture', 'technology', 'national'
}

class Category(models.Model):
    name = models.CharField(max_length=255, default="")
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, default="")
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    order = models.PositiveIntegerField(default=0, help_text="Display order in menus")
    show_in_menu = models.BooleanField(default=True, help_text="Show in top navigation bar")
    layout_type = models.CharField(
        max_length=50,
        choices=LAYOUT_CHOICES,
        default='default',
        help_text="Specifies which frontend layout to use for this category"
    )
    icon = models.CharField(max_length=100, blank=True, default="", help_text="Emoji or icon name")
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    is_system = models.BooleanField(
        default=False,
        help_text="Protected system category required for frontend routes"
    )

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['order', 'id']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name or self.parent.slug} → {self.name or self.slug}"
        return self.name or self.slug

    def clean(self):
        super().clean()
        if self.slug in SYSTEM_SLUGS:
            self.is_system = True
        if self.pk:
            original = Category.objects.filter(pk=self.pk).values('slug', 'is_system').first()
            if original and (original['slug'] in SYSTEM_SLUGS or original['is_system']):
                if self.slug != original['slug']:
                    from django.core.exceptions import ValidationError
                    raise ValidationError({'slug': f"Category '{original['slug']}' is a protected system category; its slug cannot be changed."})

    def save(self, *args, **kwargs):
        if self.slug in SYSTEM_SLUGS:
            self.is_system = True
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.slug in SYSTEM_SLUGS or self.is_system:
            from django.core.exceptions import ValidationError
            raise ValidationError(f"Category '{self.slug}' is a protected system category and cannot be deleted.")
        super().delete(*args, **kwargs)


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
        ordering = ['id']

    def __str__(self):
        return self.name or self.slug


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
    image = models.ImageField(
        upload_to="articles/",
        blank=True,
        null=True,
        verbose_name="Upload Featured Image",
        help_text="Upload article cover photo directly from your device"
    )
    featuredImage = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Featured Image URL / Path",
        help_text="Optional external image URL or static asset path (e.g. /images/...)"
    )
    imageCaption = models.CharField(max_length=255, blank=True, default="", verbose_name="Image Caption")
    meta_title = models.CharField(max_length=255, blank=True, default="", verbose_name="Meta Title")
    meta_description = models.TextField(blank=True, default="", verbose_name="Meta Description")
    
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='articles')
    category = models.ForeignKey(
        Category, 
        on_delete=models.PROTECT, 
        related_name='articles',
        limit_choices_to=~Q(layout_type__in=['stayor_hotel', 'stay'])
    )
    district = models.ForeignKey(
        'districts.District',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    publishedAt = models.DateTimeField(null=True, blank=True, verbose_name="Published At")
    updatedAt = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name="Created At")
    
    featured = models.BooleanField(default=False)
    breaking = models.BooleanField(default=False)
    popular = models.BooleanField(default=False)
    
    readTime = models.IntegerField(default=5, verbose_name="Read Time (mins)")
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ['-publishedAt', '-id']

    def __str__(self):
        return self.title or self.slug

    def save(self, *args, **kwargs):
        if self.image and not self.featuredImage:
            self.featuredImage = self.image.url
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=100)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='tags_list')

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ['id']

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
        ordering = ['-createdAt']

    def __str__(self):
        return f"Comment by {self.authorName} on {self.article_id}"


class BreakingNews(models.Model):
    text = models.CharField(max_length=500, default="")
    href = models.URLField(max_length=500)
    publishedAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Breaking News"
        verbose_name_plural = "Breaking News"
        ordering = ['-publishedAt']

    def __str__(self):
        return self.text


class HomePagePlacement(models.Model):
    section_name = models.CharField(max_length=100, unique=True)
    articles = models.ManyToManyField(Article, blank=True, related_name='home_placements')

    class Meta:
        verbose_name = "Homepage Placement"
        verbose_name_plural = "Homepage Placements"
        ordering = ['id']

    def __str__(self):
        return self.section_name


class ArticleBookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='article_bookmarks')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Article Bookmark"
        verbose_name_plural = "Article Bookmarks"
        unique_together = ('user', 'article')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} saved {self.article_id}"


class HeroSlide(models.Model):
    title = models.CharField(max_length=255, default="", verbose_name="Slide Title")
    subtitle = models.CharField(max_length=255, blank=True, default="", verbose_name="Category / Kicker", help_text="Badge or category text (e.g. परिचय, वन्यजन्तु)")
    excerpt = models.TextField(blank=True, default="", verbose_name="Slide Description / Excerpt")
    image = models.ImageField(upload_to="hero_slides/", blank=True, null=True, verbose_name="Hero Image", help_text="Custom banner image upload")
    image_url = models.CharField(max_length=500, blank=True, default="", verbose_name="Image URL / Path", help_text="Static path or external image (e.g. /images/places/khaptad_national_park.jpg)")
    article = models.ForeignKey(
        Article,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hero_slides',
        verbose_name="Linked Article",
        help_text="Optional link to a specific article"
    )
    primary_button_text = models.CharField(max_length=100, default="", blank=True, verbose_name="Primary Button Text")
    primary_button_url = models.CharField(max_length=500, default="/district", blank=True, verbose_name="Primary Button URL")
    secondary_button_text = models.CharField(max_length=100, default="", blank=True, verbose_name="Secondary Button Text")
    secondary_button_url = models.CharField(max_length=500, blank=True, default="", verbose_name="Secondary Button URL", help_text="Leave empty to trigger user contribution modal")
    order = models.PositiveIntegerField(default=0, verbose_name="Order", help_text="Display order in hero slider (0, 1, 2...)")
    is_active = models.BooleanField(default=True, verbose_name="Is Active", help_text="Show or hide on homepage")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Hero Slide"
        verbose_name_plural = "Hero Slides"
        ordering = ['order', '-id']

    def __str__(self):
        return self.title or f"Hero Slide #{self.id}"
