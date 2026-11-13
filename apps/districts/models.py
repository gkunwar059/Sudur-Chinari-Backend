from django.db import models
from django.utils.text import slugify

class District(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=255, default="")
    description = models.TextField(blank=True, default="")
    history = models.TextField(blank=True, default="")
    meta_title = models.CharField(max_length=255, blank=True, default="")
    meta_description = models.TextField(blank=True, default="")
    accentColor = models.CharField(max_length=50, blank=True, null=True)
    heroImage = models.ImageField(upload_to="districts/", blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True, default=None)
    longitude = models.FloatField(blank=True, null=True, default=None)

    class Meta:
        verbose_name = "District"
        verbose_name_plural = "Districts"
        ordering = ['slug', 'id']

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
        ordering = ['id']

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
        ordering = ['id']

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
        ordering = ['id']

    def __str__(self):
        return f"Culture for {self.district}"


class DistrictPlace(models.Model):
    CATEGORY_CHOICES = (
        ('nature', 'Nature'),
        ('heritage', 'Heritage'),
        ('spiritual', 'Spiritual / Shrine'),
        ('culture', 'Culture'),
    )

    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='places')
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    title = models.CharField(max_length=255, default="")
    description = models.TextField(default="")
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, default='nature')
    image = models.ImageField(upload_to="places/", max_length=500, blank=True, null=True)
    highlight = models.CharField(max_length=255, blank=True, null=True)

    # Rich Editorial Details
    overview = models.TextField(blank=True, default="", help_text="Detailed destination overview and significance")
    history = models.TextField(blank=True, default="", help_text="Historical, archaeological, or mythological background")

    # Geographic & Travel Facts
    location = models.CharField(max_length=255, blank=True, default="", help_text="Local area or municipality within the district")
    elevation = models.CharField(max_length=120, blank=True, default="", help_text="Altitude / elevation (e.g. 205m above sea level)")
    area_or_size = models.CharField(max_length=120, blank=True, default="", help_text="Area, length, or scale (e.g. 2,563 hectares)")
    best_time_to_visit = models.CharField(max_length=255, blank=True, default="", help_text="Recommended seasons / months to visit")
    opening_hours = models.CharField(max_length=120, blank=True, default="", help_text="Visiting hours or open access timings")
    entry_fee = models.CharField(max_length=160, blank=True, default="", help_text="Entry or permit fee details")
    weather_summary = models.CharField(max_length=160, blank=True, default="", help_text="Typical local climate / temperature (e.g. 30°C • Subtropical)")
    how_to_reach = models.TextField(blank=True, default="", help_text="Transport, highway, airport, or trail access details")
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    # Cultural Highlights & Traditions
    festivals = models.TextField(blank=True, default="", help_text="Notable festivals, jatras, or fairs associated with this place")
    local_cuisine = models.TextField(blank=True, default="", help_text="Local food, prasad, or culinary specialties nearby")
    traditions = models.TextField(blank=True, default="", help_text="Local rituals, folk arts, or cultural traditions")
    languages = models.CharField(max_length=255, blank=True, default="", help_text="Primary spoken languages or dialects in the area")

    # Travel Advisory
    travel_advisory = models.TextField(blank=True, default="", help_text="Visitor tips, local guides, clothing, or safety advice")

    class Meta:
        verbose_name = "District Place"
        verbose_name_plural = "District Places"
        ordering = ['id']

    def save(self, *args, **kwargs):
        if not self.slug:
            raw_title = getattr(self, 'title_en', None) or self.title or ''
            district_slug = self.district.slug if self.district_id and self.district else 'place'
            base = slugify(raw_title) or f"{district_slug}-place"
            base = base[:240]
            candidate = base
            counter = 1
            while DistrictPlace.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                suffix = f"-{counter}"
                candidate = f"{base[:255 - len(suffix)]}{suffix}"
                counter += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.district.name})"


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
        ordering = ['id']

    def __str__(self):
        if self.district:
            return f"{self.name} ({self.district.name})"
        return self.name


class PhotoSubmission(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    photographer_name = models.CharField(max_length=255, verbose_name="Photographer Name")
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="photo_submissions")
    title = models.CharField(max_length=255, verbose_name="Photo Title")
    description = models.TextField(blank=True, default="", verbose_name="Description")
    image = models.ImageField(upload_to="contributions/photos/", blank=True, null=True, verbose_name="Uploaded Photo")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Photo Submission"
        verbose_name_plural = "Photo Submissions"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.photographer_name} ({self.district.name})"


class StorySubmission(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    CATEGORY_CHOICES = (
        ('history', 'History / इतिहास'),
        ('culture', 'Culture / संस्कृति'),
        ('lifestyle', 'Lifestyle / जीवनशैली'),
        ('tourism', 'Tourism / पर्यटन'),
        ('folklore', 'Folklore / लोककथा'),
        ('oral_history', 'Oral History / मौखिक इतिहास'),
        ('memories', 'Memories / सम्झनाहरू'),
    )

    author_name = models.CharField(max_length=255, verbose_name="Author Name")
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name="story_submissions")
    main_category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='history')
    sub_topic = models.CharField(max_length=255, blank=True, default="")
    title = models.CharField(max_length=255, verbose_name="Story Title")
    description = models.TextField(verbose_name="Story / Knowledge Description")
    media_file = models.FileField(upload_to="contributions/stories/", blank=True, null=True, verbose_name="Picture or Audio")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User Story Submission"
        verbose_name_plural = "User Story Submissions"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.author_name} ({self.main_category})"
