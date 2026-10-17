from django.db import models

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
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='places')
    title = models.CharField(max_length=255, default="")
    description = models.TextField(default="")
    category = models.CharField(max_length=100)
    image = models.CharField(max_length=500, blank=True, null=True)
    highlight = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "District Place"
        verbose_name_plural = "District Places"
        ordering = ['id']

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
