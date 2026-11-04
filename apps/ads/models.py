from django.db import models
from django.conf import settings

class PopupAd(models.Model):
    title = models.CharField(max_length=255, default="", verbose_name="Ad Title")
    image = models.ImageField(upload_to="popup_ads/", blank=True, null=True, verbose_name="Ad Banner Image")
    image_url = models.CharField(max_length=500, blank=True, default="", help_text="Direct URL to image if not uploaded")
    target_url = models.URLField(max_length=500, blank=True, default="", verbose_name="Click Target URL")
    advertiser = models.CharField(max_length=255, blank=True, default="", verbose_name="Advertiser Name")
    duration_seconds = models.PositiveIntegerField(default=6, help_text="Display duration before auto-closing (seconds)")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Popup Roadblock Ad"
        verbose_name_plural = "Popup Roadblock Ads"
        ordering = ['-created_at', '-id']

    def __str__(self):
        return f"{self.title or 'Untitled Ad'} ({self.advertiser or 'Unknown'})"


class BannerAd(models.Model):
    PAGE_CHOICES = (
        ('all', 'All Pages / Global (सबै पृष्ठहरू)'),
        ('home', 'Homepage (गृहपृष्ठ)'),
        ('article', 'Article Detail (समाचार भित्री पृष्ठ)'),
        ('category', 'Category Pages (विधा पृष्ठ)'),
        ('district', 'District Pages (जिल्ला पृष्ठहरू)'),
        ('video', 'Video Pages (भिडियो खण्ड)'),
        ('photo', 'Photo Stories (फोटो फिचर)'),
        ('products', 'Local Products (स्थानीय उत्पादन)'),
        ('yatayat', 'Yatayat Directory (यातायात)'),
        ('sports', 'Sports Page (खेलकुद)'),
        ('politics', 'Politics Page (राजनीति)'),
        ('tourism', 'Tourism & Heritage (पर्यटन)'),
        ('stay', 'Hotels & Stay (होटल तथा बास)'),
        ('custom', 'Custom Page URL / Slug'),
    )

    PLACEMENT_CHOICES = (
        ('top-leaderboard', 'Top Leaderboard (Header - 970x90 / 728x90)'),
        ('billboard-mid', 'Billboard Mid (Between sections - 1200x120)'),
        ('sidebar', 'Sidebar Square / Rectangle (300x250 / 336x280)'),
        ('in-article', 'In-Article Banner (728x90 / 300x250)'),
        ('bottom-strip', 'Bottom Strip (Footer area - 1200x100)'),
        ('popup-roadblock', 'Popup Roadblock Splash'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending Verification (प्रमाणीकरण बाँकी)'),
        ('approved', 'Approved & Active (स्वीकृत तथा प्रकाशित)'),
        ('rejected', 'Rejected (अस्वीकृत)'),
    )

    # Core identification & creative
    title = models.CharField(max_length=255, verbose_name="Banner Title")
    page = models.CharField(
        max_length=50,
        choices=PAGE_CHOICES,
        default='all',
        db_index=True,
        verbose_name="Target Page"
    )
    custom_page_path = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Custom URL path or slug if targeting specific page (e.g. /category/economy, kailali)",
        verbose_name="Custom Target Path/Slug"
    )
    placement = models.CharField(
        max_length=50,
        choices=PLACEMENT_CHOICES,
        default='billboard-mid',
        db_index=True,
        verbose_name="Placement Position"
    )
    image = models.ImageField(upload_to="banner_ads/", blank=True, null=True, verbose_name="Banner Image")
    image_url = models.CharField(max_length=500, blank=True, default="", help_text="Direct URL to image if not uploaded")
    target_url = models.URLField(max_length=500, blank=True, default="", verbose_name="Target / Click URL")
    alt_text = models.CharField(max_length=255, blank=True, default="", verbose_name="Alt Text")
    advertiser = models.CharField(max_length=255, blank=True, default="", verbose_name="Advertiser Name")

    # Verification & Admin Control
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='approved',
        db_index=True,
        verbose_name="Verification Status"
    )
    rejection_reason = models.TextField(
        blank=True,
        default="",
        verbose_name="Rejection Reason / Admin Notes"
    )
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    priority = models.PositiveIntegerField(
        default=0,
        help_text="Higher priority ads are served first in this placement/page",
        verbose_name="Display Priority"
    )

    # User Request & Contact Info
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ad_requests",
        verbose_name="Requested By (User)"
    )
    contact_name = models.CharField(max_length=255, blank=True, default="", verbose_name="Contact Person Name")
    contact_phone = models.CharField(max_length=50, blank=True, default="", verbose_name="Contact Phone")
    contact_email = models.EmailField(blank=True, default="", verbose_name="Contact Email")
    notes = models.TextField(blank=True, default="", help_text="Notes from advertiser or campaign instructions")

    # Campaign Duration
    start_date = models.DateField(blank=True, null=True, verbose_name="Campaign Start Date")
    end_date = models.DateField(blank=True, null=True, verbose_name="Campaign End Date")

    # Analytics
    clicks_count = models.PositiveIntegerField(default=0)
    impressions_count = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Banner Advertisement"
        verbose_name_plural = "Banner Advertisements"
        ordering = ['-priority', '-created_at', '-id']

    def __str__(self):
        page_label = dict(self.PAGE_CHOICES).get(self.page, self.page)
        pos_label = dict(self.PLACEMENT_CHOICES).get(self.placement, self.placement)
        return f"[{page_label} | {pos_label}] {self.title} ({self.advertiser or 'Self'})"

