from django.db import models

class Amenity(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, help_text="Lucide icon name (e.g. Wifi, Coffee, Car)")

    class Meta:
        verbose_name = "Amenity"
        verbose_name_plural = "Amenities"
        ordering = ['name', 'id']

    def __str__(self):
        return self.name


class Hotel(models.Model):
    slug = models.SlugField(unique=True, max_length=255)
    name = models.CharField(max_length=255)
    hotel_type = models.CharField(max_length=100, help_text="e.g. Resort, Homestay, Boutique Hotel")
    category = models.ForeignKey(
        'articles.Category', 
        on_delete=models.CASCADE, 
        related_name='hotels',
        limit_choices_to={'layout_type__in': ['stayor_hotel', 'stay']}
    )
    district = models.ForeignKey(
        'districts.District', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='hotels'
    )
    
    # Location
    address = models.CharField(max_length=255)
    municipality = models.CharField(max_length=255)
    latitude = models.CharField(max_length=50, blank=True, default="")
    longitude = models.CharField(max_length=50, blank=True, default="")
    
    # Reviews
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.5)
    reviews_count = models.IntegerField(default=0)
    
    # Imagery
    hero_image = models.ImageField(upload_to="hotels/hero/")
    
    # Details & Story
    short_description = models.TextField(blank=True, default="")
    about = models.TextField()
    story = models.TextField(blank=True)
    quote_text = models.TextField(blank=True, default="")
    quote_author = models.CharField(max_length=150, blank=True, default="")
    
    # Contact
    phone1 = models.CharField(max_length=50)
    phone2 = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    
    # Amenities & Highlights
    amenities = models.ManyToManyField(Amenity, blank=True)
    highlights = models.JSONField(default=list, help_text="List of string highlights")
    
    # Reach
    map_url = models.URLField(blank=True)
    reach_bus = models.CharField(max_length=100, blank=True)
    reach_airport = models.CharField(max_length=100, blank=True)
    reach_highway = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = "Hotel"
        verbose_name_plural = "Hotels"
        ordering = ['-rating', 'id']

    def __str__(self):
        return self.name


class HotelRoom(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    name = models.CharField(max_length=100)
    guests = models.IntegerField(default=2)
    bed_type = models.CharField(max_length=100)
    image = models.ImageField(upload_to="hotels/rooms/", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = "Hotel Room"
        verbose_name_plural = "Hotel Rooms"
        ordering = ['id']

    def __str__(self):
        return f"{self.name} - {self.hotel.name}"


class HotelGallery(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to="hotels/gallery/")
    caption = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Hotel Gallery Image"
        verbose_name_plural = "Hotel Gallery Images"
        ordering = ['id']

    def __str__(self):
        return f"Gallery for {self.hotel.name} (#{self.id})"


class HotelNearbyPlace(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='nearby_places')
    name = models.CharField(max_length=255)
    distance = models.CharField(max_length=50) # e.g. 2.5 km

    class Meta:
        verbose_name = "Nearby Place"
        verbose_name_plural = "Nearby Places"
        ordering = ['id']

    def __str__(self):
        return f"{self.name} ({self.distance}) - {self.hotel.name}"
