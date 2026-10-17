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

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['order', 'id']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name or self.parent.slug} → {self.name or self.slug}"
        return self.name or self.slug


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
    featuredImage = models.CharField(max_length=500, blank=True, null=True)
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
    district = models.ForeignKey(
        'districts.District',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles'
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    publishedAt = models.DateTimeField(null=True, blank=True)
    updatedAt = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    featured = models.BooleanField(default=False)
    breaking = models.BooleanField(default=False)
    popular = models.BooleanField(default=False)
    
    readTime = models.IntegerField(default=5)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ['-publishedAt', '-id']

    def __str__(self):
        return self.title or self.slug


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
