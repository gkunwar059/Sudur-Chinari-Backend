from django.db import models

class TrendingTopic(models.Model):
    name = models.CharField(max_length=150, verbose_name="Trending Topic / Tag")
    slug = models.SlugField(max_length=150, unique=True)
    search_count = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Trending Topic"
        verbose_name_plural = "Trending Topics"
        ordering = ['order', '-search_count', 'id']

    def __str__(self):
        return self.name


class ContactInquiry(models.Model):
    INQUIRY_TYPE_CHOICES = (
        ('general', 'General Inquiry'),
        ('advertising', 'Advertising & Sponsorship'),
        ('editorial', 'Editorial Tip / Press Release'),
        ('correction', 'Correction / Feedback'),
    )

    name = models.CharField(max_length=255, verbose_name="Full Name")
    email = models.EmailField(verbose_name="Email Address")
    phone = models.CharField(max_length=50, blank=True, default="", verbose_name="Phone Number")
    subject = models.CharField(max_length=255, blank=True, default="", verbose_name="Subject")
    message = models.TextField(verbose_name="Message")
    inquiry_type = models.CharField(max_length=50, choices=INQUIRY_TYPE_CHOICES, default='general')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_inquiry_type_display()}] {self.subject or self.name} ({self.email})"


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True, verbose_name="Email Address")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Newsletter Subscriber"
        verbose_name_plural = "Newsletter Subscribers"
        ordering = ['-created_at']

    def __str__(self):
        return self.email
