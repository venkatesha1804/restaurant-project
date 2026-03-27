from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils import timezone
from datetime import timedelta


# ============================================================================
# CATEGORY MODEL
# ============================================================================

class ItemList(models.Model):
    """Restaurant menu categories (Appetizers, Mains, Desserts, etc.)"""
    
    category_name = models.CharField(
        max_length=50, 
        unique=True,
        default='Uncategorized',
        help_text="Category name (e.g., Appetizers, Main Course, Desserts)"
    )
    description = models.TextField(
        blank=True, 
        help_text="Category description"
    )
    display_order = models.IntegerField(
        default=0, 
        help_text="Order to display categories"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Hide/show this category"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'category_name']
        verbose_name_plural = "Item Lists"
        indexes = [
            models.Index(fields=['is_active', 'display_order']),
        ]

    def __str__(self):
        return self.category_name

    def get_active_items_count(self):
        """Get count of active items in this category"""
        return self.items.filter(is_available=True).count()


# ============================================================================
# MENU ITEMS MODEL
# ============================================================================

class Items(models.Model):
    """Menu items with pricing and images"""
    
    item_name = models.CharField(
        max_length=100,
        default='Unknown Item',
        help_text="Name of the menu item"
    )
    description = models.TextField(
        blank=False,
        default='',
        help_text="Detailed description of the item"
    )
    price = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Price of the item"
    )
    category = models.ForeignKey(
        ItemList, 
        related_name='items',
        on_delete=models.CASCADE,
        help_text="Category this item belongs to"
    )
    image = models.ImageField(
        upload_to='items/',
        default='items/default.png',
        help_text="Item image"
    )
    is_available = models.BooleanField(
        default=True,
        help_text="Is this item available for ordering?"
    )
    is_vegetarian = models.BooleanField(
        default=False,
        help_text="Is this item vegetarian?"
    )
    is_vegan = models.BooleanField(
        default=False,
        help_text="Is this item vegan?"
    )
    is_spicy = models.BooleanField(
        default=False,
        help_text="Is this item spicy?"
    )
    preparation_time = models.IntegerField(
        default=15,
        validators=[MinValueValidator(1)],
        help_text="Estimated preparation time in minutes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'item_name']
        indexes = [
            models.Index(fields=['category', 'is_available']),
            models.Index(fields=['is_available']),
        ]
        verbose_name_plural = "Items"

    def __str__(self):
        return f"{self.item_name} - ₹{self.price}"

    def get_dietary_tags(self):
        """Get dietary tags for this item"""
        tags = []
        if self.is_vegetarian:
            tags.append("Vegetarian")
        if self.is_vegan:
            tags.append("Vegan")
        if self.is_spicy:
            tags.append("Spicy")
        return tags


# ============================================================================
# ABOUT US MODEL
# ============================================================================

class AboutUs(models.Model):
    """Restaurant information page"""
    
    description = models.TextField(
        blank=False,
        default='',
        help_text="Restaurant description and about information"
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number')],
        help_text="Contact phone number"
    )
    email = models.EmailField(
        blank=True,
        help_text="Contact email address"
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        help_text="Restaurant physical address"
    )
    opening_hours = models.CharField(
        max_length=100,
        blank=True,
        help_text="Opening hours (e.g., 10:00 AM - 10:00 PM)"
    )
    latitude = models.FloatField(
        blank=True,
        null=True,
        help_text="Latitude for map"
    )
    longitude = models.FloatField(
        blank=True,
        null=True,
        help_text="Longitude for map"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "About Us"

    def __str__(self):
        return "Restaurant Information"


# ============================================================================
# FEEDBACK/REVIEW MODEL
# ============================================================================

class Feedback(models.Model):
    """Customer reviews and feedback"""
    
    RATING_CHOICES = [
        (1, '⭐ Poor'),
        (2, '⭐⭐ Fair'),
        (3, '⭐⭐⭐ Good'),
        (4, '⭐⭐⭐⭐ Very Good'),
        (5, '⭐⭐⭐⭐⭐ Excellent'),
    ]

    user_name = models.CharField(
        max_length=100,
        default='Anonymous',
        help_text="Name of the reviewer"
    )
    email = models.EmailField(
        help_text="Email of the reviewer"
    )
    description = models.TextField(
        blank=False,
        help_text="Detailed review/feedback"
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1-5"
    )
    image = models.ImageField(
        upload_to='feedback/',
        blank=True,
        null=True,
        help_text="Optional image from reviewer"
    )
    is_approved = models.BooleanField(
        default=False,
        help_text="Has this review been approved?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_approved', '-created_at']),
        ]
        verbose_name_plural = "Feedback"

    def __str__(self):
        return f"{self.user_name} - {self.rating} stars"

    def get_rating_display_stars(self):
        """Get star representation of rating"""
        return "⭐" * self.rating


# ============================================================================
# TABLE BOOKING MODEL
# ============================================================================

class BookTable(models.Model):
    """Table booking system"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending Confirmation'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]

    name = models.CharField(
        max_length=100,
        help_text="Customer name"
    )
    email = models.EmailField(
        help_text="Customer email address"
    )
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number')],
        help_text="Customer contact number"
    )
    total_persons = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        help_text="Number of people (1-20)"
    )
    booking_date = models.DateField(
        help_text="Date of booking"
    )
    booking_time = models.TimeField(
        default='19:00',
        help_text="Preferred booking time"
    )
    special_requests = models.TextField(
        blank=True,
        help_text="Any special requirements (e.g., high chair, allergy info)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current booking status"
    )
    confirmation_sent = models.BooleanField(
        default=False,
        help_text="Has confirmation email been sent?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['booking_date', 'status']),
            models.Index(fields=['status', '-created_at']),
        ]
        verbose_name_plural = "Table Bookings"

    def __str__(self):
        return f"{self.name} - {self.booking_date} at {self.booking_time}"

    def is_upcoming(self):
        """Check if booking is in the future"""
        from datetime import datetime
        booking_datetime = datetime.combine(self.booking_date, self.booking_time)
        booking_datetime = timezone.make_aware(booking_datetime)
        return booking_datetime > timezone.now()

    def is_today(self):
        """Check if booking is today"""
        return self.booking_date == timezone.now().date()

    def get_time_until_booking(self):
        """Get time remaining until booking"""
        from datetime import datetime
        booking_datetime = datetime.combine(self.booking_date, self.booking_time)
        booking_datetime = timezone.make_aware(booking_datetime)
        time_diff = booking_datetime - timezone.now()
        return time_diff

    def can_cancel(self):
        """Check if booking can be cancelled (at least 2 hours before)"""
        if not self.is_upcoming():
            return False
        time_until = self.get_time_until_booking()
        return time_until > timedelta(hours=2)

    def mark_completed(self):
        """Mark booking as completed"""
        self.status = 'completed'
        self.save()

    def mark_no_show(self):
        """Mark booking as no-show"""
        self.status = 'no_show'
        self.save()


# ============================================================================
# FAVORITE ITEMS MODEL (NEW FEATURE)
# ============================================================================

class FavoriteItem(models.Model):
    """User's favorite items (wishlist)"""
    
    user_ip = models.CharField(
        max_length=100,
        help_text="IP address of user (for anonymous users)"
    )
    item = models.ForeignKey(
        Items,
        related_name='favorites',
        on_delete=models.CASCADE,
        help_text="Favorite item"
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_ip', 'item')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user_ip} - {self.item.item_name}"


# ============================================================================
# SPECIAL OFFERS MODEL (NEW FEATURE)
# ============================================================================

class SpecialOffer(models.Model):
    """Special offers and promotions"""
    
    title = models.CharField(
        max_length=100,
        help_text="Offer title"
    )
    description = models.TextField(
        help_text="Detailed offer description"
    )
    discount_percentage = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Discount percentage"
    )
    valid_from = models.DateTimeField(
        help_text="Offer start date and time"
    )
    valid_until = models.DateTimeField(
        help_text="Offer end date and time"
    )
    applicable_items = models.ManyToManyField(
        Items,
        blank=True,
        help_text="Items this offer applies to (leave empty for all)"
    )
    image = models.ImageField(
        upload_to='offers/',
        blank=True,
        help_text="Offer banner image"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is this offer currently active?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-valid_from']
        indexes = [
            models.Index(fields=['is_active', '-valid_from']),
        ]

    def __str__(self):
        return f"{self.title} - {self.discount_percentage}% off"

    def is_currently_valid(self):
        """Check if offer is currently valid"""
        now = timezone.now()
        return self.is_active and self.valid_from <= now <= self.valid_until


# ============================================================================
# BOOKING NOTIFICATION MODEL (NEW FEATURE)
# ============================================================================

class BookingNotification(models.Model):
    """Track booking notifications sent to customers"""
    
    NOTIFICATION_TYPE_CHOICES = [
        ('confirmation', 'Booking Confirmation'),
        ('reminder_24h', '24 Hour Reminder'),
        ('reminder_2h', '2 Hour Reminder'),
        ('cancellation', 'Cancellation'),
        ('completion', 'Booking Completed'),
    ]

    booking = models.ForeignKey(
        BookTable,
        related_name='notifications',
        on_delete=models.CASCADE,
        help_text="Related booking"
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE_CHOICES,
        help_text="Type of notification"
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(
        default=True,
        help_text="Was notification sent successfully?"
    )
    error_message = models.TextField(
        blank=True,
        help_text="Error message if sending failed"
    )

    class Meta:
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['booking', 'notification_type']),
        ]

    def __str__(self):
        return f"{self.booking.name} - {self.get_notification_type_display()}"

        # ============================================================================
# SHOPPING CART MODELS
# ============================================================================

class Cart(models.Model):
    """Shopping cart for users"""
    
    user = models.OneToOneField(
        'auth.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cart',
        help_text="User who owns this cart"
    )
    session_key = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        help_text="Session key for anonymous users"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Carts"

    def __str__(self):
        if self.user:
            return f"Cart of {self.user.username}"
        return f"Anonymous Cart ({self.session_key})"

    def get_total_price(self):
        """Calculate total cart price"""
        total = sum(item.get_subtotal() for item in self.items.all())
        return total

    def get_total_items(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items.all())

    def get_total_quantity(self):
        """Get count of unique items"""
        return self.items.count()

    def clear_cart(self):
        """Clear all items from cart"""
        self.items.all().delete()


class CartItem(models.Model):
    """Individual items in the cart"""
    
    cart = models.ForeignKey(
        Cart,
        related_name='items',
        on_delete=models.CASCADE,
        help_text="Shopping cart this item belongs to"
    )
    item = models.ForeignKey(
        Items,
        on_delete=models.CASCADE,
        help_text="Menu item in cart"
    )
    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Quantity of this item"
    )
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cart', 'item')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.item.item_name} x {self.quantity}"

    def get_subtotal(self):
        """Calculate subtotal for this cart item"""
        return self.item.price * self.quantity

    def increase_quantity(self, amount=1):
        """Increase item quantity"""
        self.quantity += amount
        self.save()

    def decrease_quantity(self, amount=1):
        """Decrease item quantity"""
        if self.quantity > amount:
            self.quantity -= amount
            self.save()
        else:
            self.delete()


            # ============================================================================
# ORDER MODEL
# ============================================================================

class Order(models.Model):
    """Customer food orders"""
    
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready for Pickup'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    DELIVERY_TYPE_CHOICES = [
        ('delivery', 'Home Delivery'),
        ('pickup', 'Pickup'),
    ]

    # Customer Info
    customer_name = models.CharField(
        max_length=100,
        help_text="Customer full name"
    )
    customer_email = models.EmailField(
        help_text="Customer email address"
    )
    customer_phone = models.CharField(
        max_length=15,
        help_text="Customer phone number"
    )

    # Delivery Info
    delivery_type = models.CharField(
        max_length=20,
        choices=DELIVERY_TYPE_CHOICES,
        default='delivery',
        help_text="Delivery or Pickup"
    )
    delivery_address = models.TextField(
        help_text="Full delivery address"
    )
    delivery_city = models.CharField(
        max_length=50,
        default='Bangalore',
        help_text="City for delivery"
    )
    delivery_pincode = models.CharField(
        max_length=10,
        help_text="Pincode/Postal code"
    )

    # Order Details
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Total order amount"
    )
    special_requests = models.TextField(
        blank=True,
        help_text="Special instructions (allergies, preferences, etc.)"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pending',
        help_text="Order status"
    )
    
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending',
        help_text="Payment status"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estimated_delivery = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Estimated delivery time"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['customer_email', '-created_at']),
        ]

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"

    def get_total_items(self):
        """Get total number of items in order"""
        return sum(item.quantity for item in self.items.all())

    def get_status_display_badge(self):
        """Get colored badge for status"""
        colors = {
            'pending': 'warning',
            'confirmed': 'info',
            'preparing': 'primary',
            'ready': 'success',
            'delivered': 'success',
            'cancelled': 'danger',
        }
        return colors.get(self.status, 'secondary')

    def mark_confirmed(self):
        """Mark order as confirmed"""
        self.status = 'confirmed'
        self.save()

    def mark_preparing(self):
        """Mark order as preparing"""
        self.status = 'preparing'
        self.save()

    def mark_ready(self):
        """Mark order as ready"""
        self.status = 'ready'
        self.save()

    def mark_delivered(self):
        """Mark order as delivered"""
        self.status = 'delivered'
        self.save()


class OrderItem(models.Model):
    """Individual items in an order"""
    
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE,
        help_text="Order this item belongs to"
    )
    item = models.ForeignKey(
        Items,
        on_delete=models.CASCADE,
        help_text="Menu item ordered"
    )
    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Quantity ordered"
    )
    price_at_purchase = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Item price at time of order"
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Subtotal for this item"
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.item.item_name} x {self.quantity}"

    def save(self, *args, **kwargs):
        """Calculate subtotal before saving"""
        self.subtotal = self.price_at_purchase * self.quantity
        super().save(*args, **kwargs)