from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from PIL import Image
import os


class UserProfile(models.Model):
    """Extended user profile with role and additional information"""
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('advertiser', 'Advertiser'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.role})"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize profile picture if it exists
        if self.profile_picture:
            img = Image.open(self.profile_picture.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.profile_picture.path)


class Category(models.Model):
    """Travel offer categories"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name


class TravelOffer(models.Model):
    """Travel offers posted by advertisers"""
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    advertiser = models.ForeignKey(User, on_delete=models.CASCADE, related_name='travel_offers')
    
    # Pricing and availability
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percentage = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True, blank=True
    )
    available_spots = models.PositiveIntegerField()
    
    # Location and timing
    destination = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Media
    image = models.ImageField(upload_to='offer_images/', blank=True, null=True)
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def is_available(self):
        """Check if offer is still available for booking"""
        from django.utils import timezone
        return (
            self.status == 'approved' and 
            self.available_spots > 0 and 
            self.start_date > timezone.now().date()
        )
    
    @property
    def discount_amount(self):
        """Calculate discount amount if applicable"""
        if self.original_price and self.discount_percentage:
            return self.original_price * (self.discount_percentage / 100)
        return 0
    
    def save(self, *args, **kwargs):
        # Calculate price based on discount
        if self.original_price and self.discount_percentage:
            self.price = self.original_price - self.discount_amount
        
        super().save(*args, **kwargs)
        
        # Resize image if it exists
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 800 or img.width > 800:
                output_size = (800, 800)
                img.thumbnail(output_size)
                img.save(self.image.path)


class Booking(models.Model):
    """Student bookings for travel offers"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    offer = models.ForeignKey(TravelOffer, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Contact information
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField()
    special_requests = models.TextField(blank=True)
    
    # Pricing snapshot
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'offer')
        ordering = ['-booking_date']
    
    def __str__(self):
        return f"{self.student.username} - {self.offer.title}"


class Message(models.Model):
    """Messages between students and advertisers"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    offer = models.ForeignKey(TravelOffer, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    
    subject = models.CharField(max_length=200)
    body = models.TextField()
    
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"From {self.sender.username} to {self.recipient.username}: {self.subject}"


class Favourite(models.Model):
    """Student favourite offers"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favourites')
    offer = models.ForeignKey(TravelOffer, on_delete=models.CASCADE, related_name='favourited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'offer')
    
    def __str__(self):
        return f"{self.student.username} favourited {self.offer.title}"


class Review(models.Model):
    """Student reviews for completed bookings"""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review for {self.booking.offer.title} by {self.booking.student.username}"
