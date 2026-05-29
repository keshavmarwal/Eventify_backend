from django.db import models
from django.conf import settings
 
 
class Category(models.Model):
    # \"\"\"Event category: Movies, Cricket, Shows, etc.\"\"\"
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)    # URL-friendly version: 'live-music'
    icon = models.CharField(max_length=10)  # Emoji icon
    
    class Meta:
        verbose_name_plural = 'categories'
    
    def __str__(self):
        return self.name
 
 
class Event(models.Model):
    # \"\"\"Main event model.\"\"\"
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('cancelled', 'Cancelled'),
        ('sold_out', 'Sold Out'),
    ]
    
    # Basic Info
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='events')
    
    # Venue & Time
    venue = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    address = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    
    # Pricing & Tickets
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_seats = models.PositiveIntegerField()
    
    # 📘 LEARN: @property creates a computed field (not stored in DB)
    # calculated on the fly from other data
    @property
    def available_seats(self):
        booked = self.bookings.filter(status='confirmed').aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
        return self.total_seats - booked
    
    @property
    def is_sold_out(self):
        return self.available_seats <= 0
    
    # Media
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    tags = models.CharField(max_length=500, blank=True)  # Comma-separated
    
    # Meta
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.0)
    badge = models.CharField(max_length=50, blank=True)  # 'Hot', 'Trending', etc.
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['date', 'time']   # 📘 Default sort order for queries
        indexes = [
            models.Index(fields=['date', 'city']),      # Speed up date+city queries
            models.Index(fields=['category', 'status']), # Speed up category filter
        ]
    
    def __str__(self):
        return f"{self.title} - {self.date}"
 
 
class Booking(models.Model):
    # \"\"\"A user's booking for an event.\"\"\"
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    # 📘 LEARN: ForeignKey creates a many-to-one relationship.
    # on_delete=CASCADE means if the user is deleted, their bookings are too.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='bookings'  # user.bookings.all() to get all bookings
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='bookings'  # event.bookings.all() to get all bookings
    )
    
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    
    # Booking reference number (shown to user after booking)
    reference = models.CharField(max_length=20, unique=True)
    
    booked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-booked_at']
        # 📘 LEARN: unique_together prevents duplicate bookings
        # (comment out if you want multiple bookings per user per event)
        # unique_together = [['user', 'event']]
    
    def save(self, *args, **kwargs):
        # Auto-calculate total price and generate reference on first save
        if not self.pk:
            self.total_price = self.event.price * self.quantity
            import uuid
            self.reference = f"EVT-{str(uuid.uuid4()).upper()[:8]}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} → {self.event.title} ({self.quantity}x)"
