from django.db import models

class ProductCategory(models.Model):
    name = models.CharField(max_length=255, default="", verbose_name="Category Name")
    slug = models.SlugField(unique=True, max_length=150)
    icon = models.CharField(max_length=100, blank=True, default="", help_text="Emoji or icon name (e.g. 🥛, 🌾, 🍎)")
    order = models.PositiveIntegerField(default=0, help_text="Display order in filters")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"
        ordering = ['order', 'id']

    def __str__(self):
        return self.name or self.slug


class LocalProduct(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    name = models.CharField(max_length=255, default="", verbose_name="Product Name")
    slug = models.SlugField(unique=True, max_length=200)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')
    district = models.ForeignKey('districts.District', on_delete=models.CASCADE, related_name='local_products')
    description = models.TextField(blank=True, default="", verbose_name="Product Description")
    farmer_name = models.CharField(max_length=255, blank=True, default="", verbose_name="Farmer / Business Name")
    contact_phone = models.CharField(max_length=50, blank=True, default="", verbose_name="Contact Number")
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    image_url = models.CharField(max_length=500, blank=True, default="", help_text="External URL if image not uploaded directly")
    seasonality = models.CharField(max_length=255, blank=True, default="", help_text="e.g. All Year, Autumn, Winter")
    estimated_price_range = models.CharField(max_length=150, blank=True, default="", help_text="e.g. Rs. 800 - 1000 / kg")
    unit = models.CharField(max_length=50, blank=True, default="kg", help_text="e.g. kg, litre, piece")
    is_featured = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Local Product"
        verbose_name_plural = "Local Products"
        ordering = ['-is_featured', 'name', 'id']

    def __str__(self):
        return f"{self.name} ({self.district.name if self.district else 'No district'})"


class ProductProducer(models.Model):
    name = models.CharField(max_length=255, verbose_name="Producer / Farmer Name")
    district = models.ForeignKey('districts.District', on_delete=models.CASCADE, related_name='producers')
    municipality_address = models.CharField(max_length=255, blank=True, default="", help_text="e.g. Sanfebagar - 3, Achham")
    phone = models.CharField(max_length=50, blank=True, default="")
    experience_years = models.CharField(max_length=50, blank=True, default="", help_text="e.g. 12 Years")
    avatar = models.ImageField(upload_to="producers/", blank=True, null=True)
    avatar_url = models.CharField(max_length=500, blank=True, default="")
    products = models.ManyToManyField(LocalProduct, related_name='producers', blank=True)
    bio = models.TextField(blank=True, default="")
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Product Producer / Farmer"
        verbose_name_plural = "Product Producers / Farmers"
        ordering = ['name', 'id']

    def __str__(self):
        return f"{self.name} ({self.municipality_address or self.district.name})"

