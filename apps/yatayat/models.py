from django.db import models

class TransportLocation(models.Model):
    name = models.CharField(max_length=255, verbose_name="Location / Station Name")
    district = models.ForeignKey('districts.District', on_delete=models.CASCADE, related_name='transport_locations')
    is_hub = models.BooleanField(default=False, help_text="Major hub (e.g. Dhangadhi, Attariya, Mahendranagar)")
    phone = models.CharField(max_length=50, blank=True, default="")
    helpdesk_contact = models.CharField(max_length=50, blank=True, default="")
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name = "Transport Hub / Location"
        verbose_name_plural = "Transport Hubs / Locations"
        ordering = ['-is_hub', 'name', 'id']

    def __str__(self):
        return f"{self.name} ({self.district.name})"


class TransportService(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    SERVICE_TYPE_CHOICES = (
        ('bus', 'Bus'),
        ('hiace', 'Hiace'),
        ('jeep', 'Jeep'),
    )
    BADGE_COLOR_CHOICES = (
        ('emerald', 'Emerald'),
        ('blue', 'Blue'),
        ('amber', 'Amber'),
        ('brand', 'Brand Green'),
    )

    title = models.CharField(max_length=255, verbose_name="Company / Operator Name")
    sub_title = models.CharField(max_length=255, blank=True, default="", verbose_name="Service Description / Subtitle")
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES, default='bus')
    badge_text = models.CharField(max_length=100, blank=True, default="नियमित सेवा", help_text="e.g. लोकप्रिय, नियमित सेवा, सुपर डिलक्स")
    badge_color = models.CharField(max_length=20, choices=BADGE_COLOR_CHOICES, default='emerald')
    
    origin_name = models.CharField(max_length=150, verbose_name="Origin (e.g. साँफेबगर / Sanfebagar)")
    destination_name = models.CharField(max_length=150, verbose_name="Destination (e.g. धनगढी / Dhangadhi)")
    route_stops = models.JSONField(default=list, blank=True, help_text="List of intermediate stops [\"Attariya\", \"Dipayal\"]")
    
    departure_time = models.CharField(max_length=100, blank=True, default="", verbose_name="Departure Time")
    estimated_fare = models.CharField(max_length=100, blank=True, default="", verbose_name="Estimated Fare (e.g. रु. १,२००)")
    total_seats = models.CharField(max_length=50, blank=True, default="36", verbose_name="Seats Count")
    contact_phone = models.CharField(max_length=50, blank=True, default="", verbose_name="Contact Phone")
    contact_numbers = models.JSONField(default=list, blank=True, help_text="List of contact phone numbers [\"98580-xxxxx\"]")
    
    image = models.ImageField(upload_to="yatayat/", blank=True, null=True)
    image_url = models.CharField(max_length=500, blank=True, default="")
    notes = models.TextField(blank=True, default="", verbose_name="Amenities & Notes")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')
    verified = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Transport Service / Route"
        verbose_name_plural = "Transport Services / Routes"
        ordering = ['-verified', 'service_type', 'title']

    def __str__(self):
        return f"[{self.get_service_type_display()}] {self.title}: {self.origin_name} -> {self.destination_name}"


class TransportReport(models.Model):
    service = models.ForeignKey(TransportService, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports')
    issue_type = models.CharField(max_length=100, default='inaccurate_info')
    description = models.TextField()
    reporter_phone = models.CharField(max_length=50, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Transport Report / Feedback"
        verbose_name_plural = "Transport Reports / Feedback"
        ordering = ['-created_at']

    def __str__(self):
        return f"Report {self.id} on {self.service or 'General'}"


class EmergencyHelpline(models.Model):
    CATEGORY_CHOICES = (
        ('traffic', 'Traffic Police'),
        ('buspark', 'Bus Park Counter'),
        ('helpdesk', 'Helpdesk / Junction'),
        ('police', 'Nepal Police'),
    )

    title = models.CharField(max_length=255, verbose_name="Helpline Title")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='traffic')
    district = models.ForeignKey('districts.District', on_delete=models.SET_NULL, null=True, blank=True, help_text="Null for province-wide")
    phone_number = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=150, blank=True, default="", help_text="e.g. 24/7 Toll Free, Central Junction")
    is_24_7 = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Emergency Helpline / Hotlines"
        verbose_name_plural = "Emergency Helplines / Hotlines"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.title} ({self.phone_number})"
