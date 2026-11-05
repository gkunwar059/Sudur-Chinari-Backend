from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class VideoItem(models.Model):
    title = models.CharField(max_length=255, default="")
    thumbnail = models.ImageField(
        upload_to="videos/thumbnails/",
        blank=True,
        null=True,
        max_length=500,
        verbose_name="Thumbnail Image",
        help_text="Upload video thumbnail directly from your device"
    )
    video_url = models.CharField(max_length=500, blank=True, default="", help_text="Direct MP4 or streaming video URL")
    youtube_id = models.CharField(max_length=100, blank=True, default="", help_text="YouTube Video ID (e.g. jNQXAC9IVRw)")
    duration = models.CharField(max_length=20)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    publishedAt = models.DateTimeField()
    district = models.ForeignKey('districts.District', on_delete=models.SET_NULL, null=True, blank=True)
    isShort = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Video"
        verbose_name_plural = "Videos"
        ordering = ['-publishedAt']

    def __str__(self):
        return self.title


class VideoComment(models.Model):
    video = models.ForeignKey(VideoItem, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    authorName = models.CharField(max_length=255)
    authorLocation = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Video Comment"
        verbose_name_plural = "Video Comments"
        ordering = ['-createdAt']

    def __str__(self):
        return f"Comment by {self.authorName} on {self.video_id}"


class VideoLike(models.Model):
    video = models.ForeignKey(VideoItem, on_delete=models.CASCADE, related_name='user_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Video Like"
        verbose_name_plural = "Video Likes"
        unique_together = ('video', 'user')

    def __str__(self):
        return f"{self.user} likes video {self.video_id}"


class VideoCommentLike(models.Model):
    comment = models.ForeignKey(VideoComment, on_delete=models.CASCADE, related_name='user_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_comment_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Video Comment Like"
        verbose_name_plural = "Video Comment Likes"
        unique_together = ('comment', 'user')

    def __str__(self):
        return f"{self.user} likes comment {self.comment_id}"


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


class PhotoStoryImage(models.Model):
    story = models.ForeignKey(PhotoStory, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to="photo_stories/", blank=True, null=True)
    image_url = models.CharField(max_length=500, blank=True, default="")
    caption = models.CharField(max_length=500, blank=True, default="")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Photo Story Gallery Image"
        verbose_name_plural = "Photo Story Gallery Images"
        ordering = ['order', 'id']

    def __str__(self):
        return f"Image #{self.id} for {self.story.title}"
