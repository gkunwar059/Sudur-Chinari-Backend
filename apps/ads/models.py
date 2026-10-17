from django.db import models

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
