from django.db import models

class VideoItem(models.Model):
    title = models.CharField(max_length=255, default="")
    thumbnail = models.URLField(max_length=500)
    duration = models.CharField(max_length=20)
    views = models.IntegerField(default=0)
    publishedAt = models.DateTimeField()
    district = models.ForeignKey('districts.District', on_delete=models.SET_NULL, null=True, blank=True)
    isShort = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Video"
        verbose_name_plural = "Videos"
        ordering = ['-publishedAt']

    def __str__(self):
        return self.title


class PhotoStory(models.Model):
    title = models.CharField(max_length=255, default="")
    description = models.TextField(default="")
    coverImage = models.URLField(max_length=500)
    imageCount = models.IntegerField(default=1)
    photographer = models.CharField(max_length=255)
    publishedAt = models.DateTimeField()
    district = models.ForeignKey('districts.District', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Photo Story"
        verbose_name_plural = "Photo Stories"
        ordering = ['-publishedAt']

    def __str__(self):
        return self.title
