from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils import timezone
from datetime import timedelta


CANCELLABLE_STATUSES = ["pending", "confirmed"]


# ============================================================================
# CATEGORY MODEL
# ============================================================================

class ItemList(models.Model):
    """Restaurant menu categories"""

    category_name = models.CharField(
        max_length=50,
        unique=True,
        default="Uncategorized",
        help_text="Category name",
    )
    description = models.TextField(blank=True, help_text="Category description")
    display_order = models.IntegerField(default=0, help_text="Order to display")
    is_active = models.BooleanField(default=True, help_text="Active?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "category_name"]
        verbose_name_plural = "Item Lists"
        indexes = [models.Index(fields=["is_active", "display_order"])]

    def __str__(self):
        return self.category_name


# ============================================================================
# MENU ITEMS MODEL
# ============================================================================

class Items(models.Model):
    """Menu items with pricing and images"""

    item_name = models.CharField(max_length=100, default="Unknown Item")
    description = models.TextField(blank=False, default="")
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    category = models.ForeignKey(
        ItemList,
        related_name="items",
        on_delete=models.CASCADE,
    )
    image = models.ImageField(
        upload_to="items/",
        default="items/default.png",
    )
    is_available = models.BooleanField(default=True)
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_spicy = models.BooleanField(default=False)
    preparation_time = models.IntegerField(
        default=15,
        validators=[MinValueValidator(1)],
    )

    stock_quantity = models.IntegerField(
        default=100,
        validators=[MinValueValidator(0)],
    )
    track_inventory = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["category", "item_name"]
        indexes = [
            models.Index(fields=["category", "is_available"]),
            models.Index(fields=["is_available"]),
        ]
        verbose_name_plural = "Items"

    def __str__(self):
        return f"{self.item_name} - ₹{self.price}"

    def is_in_stock(self, quantity=1):
        if not self.track_inventory:
            return True
        return self.stock_quantity >= quantity

    def reduce_stock(self, quantity):
        if self.track_inventory:
            self.stock_quantity = max(0, self.stock_quantity - quantity)
            self.save(update_fields=["stock_quantity"])


# ============================================================================
# ABOUT US MODEL
# ============================================================================

class AboutUs(models.Model):
    """Restaurant information page"""

    description = models.TextField(blank=False, default="")
    phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[RegexValidator(r"^\+?1?\d{9,15}$", "Enter valid phone")],
    )
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    opening_hours = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
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
        (1, "⭐ Poor"),
        (2, "⭐⭐ Fair"),
        (3, "⭐⭐⭐ Good"),
        (4, "⭐⭐⭐⭐ Very Good"),
        (5, "⭐⭐⭐⭐⭐ Excellent"),
    ]

    user_name = models.CharField(max_length=100, default="Anonymous")
    email = models.EmailField()
    description = models.TextField(blank=False)
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    image = models.ImageField(upload_to="feedback/", blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["is_approved", "-created_at"])]
        verbose_name_plural = "Feedback"

    def __str__(self):
        return f"{self.user_name} - {self.rating} stars"


# ============================================================================
# TABLE BOOKING MODEL
# ============================================================================

class BookTable(models.Model):
    """Table booking system"""

    STATUS_CHOICES = [
        ("pending", "Pending Confirmation"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
        ("no_show", "No Show"),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r"^\+?1?\d{9,15}$", "Enter valid phone")],
    )
    total_persons = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    booking_date = models.DateField()
    booking_time = models.TimeField(default="19:00")
    special_requests = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    confirmation_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["booking_date", "status"]),
            models.Index(fields=["status", "-created_at"]),
        ]
        verbose_name_plural = "Table Bookings"

    def __str__(self):
        return f"{self.name} - {self.booking_date} at {self.booking_time}"

    def can_be_cancelled(self):
        return self.status in CANCELLABLE_STATUSES


# ============================================================================
# FAVORITE ITEMS MODEL
# ============================================================================

class FavoriteItem(models.Model):
    """User's favorite items"""

    user_ip = models.CharField(max_length=100)
    item = models.ForeignKey(Items, related_name="favorites", on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user_ip", "item")
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user_ip} - {self.item.item_name}"


# ============================================================================
# SPECIAL OFFERS MODEL
# ============================================================================

class SpecialOffer(models.Model):
    """Special offers and promotions"""

    title = models.CharField(max_length=100)
    description = models.TextField()
    discount_percentage = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    applicable_items = models.ManyToManyField(Items, blank=True)
    image = models.ImageField(upload_to="offers/", blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-valid_from"]
        indexes = [models.Index(fields=["is_active", "-valid_from"])]

    def __str__(self):
        return f"{self.title} - {self.discount_percentage}% off"


# ============================================================================
# BOOKING NOTIFICATION MODEL
# ============================================================================

class BookingNotification(models.Model):
    """Track booking notifications"""

    NOTIFICATION_TYPE_CHOICES = [
        ("confirmation", "Booking Confirmation"),
        ("reminder_24h", "24 Hour Reminder"),
        ("reminder_2h", "2 Hour Reminder"),
        ("cancellation", "Cancellation"),
        ("completion", "Booking Completed"),
    ]

    booking = models.ForeignKey(
        BookTable, related_name="notifications", on_delete=models.CASCADE
    )
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPE_CHOICES
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-sent_at"]
        indexes = [models.Index(fields=["booking", "notification_type"])]

    def __str__(self):
        return f"{self.booking.name} - {self.get_notification_type_display()}"


# ============================================================================
# SHOPPING CART MODELS
# ============================================================================

class Cart(models.Model):
    """Shopping cart for users"""

    user = models.OneToOneField(
        "auth.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cart",
    )
    session_key = models.CharField(max_length=40, blank=True, null=True)
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
        return sum(item.quantity for item in self.items.all())

    def get_total_quantity(self):
        """Get count of unique items"""
        return self.items.count()

    def clear_cart(self):
        """Clear all items from cart"""
        self.items.all().delete()


class CartItem(models.Model):
    """Individual items in the cart"""

    cart = models.ForeignKey(Cart, related_name="items", on_delete=models.CASCADE)
    item = models.ForeignKey(Items, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("cart", "item")
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.item.item_name} x {self.quantity}"

    def get_subtotal(self):
        """Calculate subtotal for this cart item"""
        return self.item.price * self.quantity


# ============================================================================
# ORDER MODELS
# ============================================================================

class Order(models.Model):
    """Customer food orders"""

    ORDER_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("preparing", "Preparing"),
        ("ready", "Ready for Pickup"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    DELIVERY_TYPE_CHOICES = [
        ("delivery", "Home Delivery"),
        ("pickup", "Pickup"),
    ]

    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    delivery_type = models.CharField(
        max_length=20, choices=DELIVERY_TYPE_CHOICES, default="delivery"
    )
    delivery_address = models.TextField()
    delivery_city = models.CharField(max_length=50, default="Bangalore")
    delivery_pincode = models.CharField(max_length=10)
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    special_requests = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=ORDER_STATUS_CHOICES, default="pending"
    )
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("completed", "Completed"),
            ("failed", "Failed"),
            ("refund_pending", "Refund Pending"),
            ("refunded", "Refunded"),
        ],
        default="pending",
    )
    coupon_code = models.CharField(max_length=20, blank=True)
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estimated_delivery = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["customer_email", "-created_at"]),
        ]

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"

    def get_total_items(self):
        """Get total number of items in order"""
        return sum(item.quantity for item in self.items.all())

    def can_be_cancelled(self):
        return self.status in CANCELLABLE_STATUSES


class OrderItem(models.Model):
    """Individual items in an order"""

    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    item = models.ForeignKey(Items, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    price_at_purchase = models.DecimalField(max_digits=8, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.item.item_name} x {self.quantity}"

    def save(self, *args, **kwargs):
        """Calculate subtotal before saving"""
        self.subtotal = self.price_at_purchase * self.quantity
        super().save(*args, **kwargs)


# ============================================================================
# ITEM RATING MODEL
# ============================================================================

class ItemRating(models.Model):
    """Customer ratings and reviews for menu items"""

    RATING_CHOICES = [
        (1, "⭐ Poor"),
        (2, "⭐⭐ Fair"),
        (3, "⭐⭐⭐ Good"),
        (4, "⭐⭐⭐⭐ Very Good"),
        (5, "⭐⭐⭐⭐⭐ Excellent"),
    ]

    item = models.ForeignKey(
        Items, related_name="itemrating_set", on_delete=models.CASCADE
    )
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    review = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["item", "is_approved"])]
        unique_together = ("item", "customer_email")

    def __str__(self):
        return f"{self.customer_name} - {self.item.item_name} ({self.rating}★)"


# ============================================================================
# FEATURE 1: WISHLIST
# ============================================================================

class Wishlist(models.Model):
    """User's wishlist - items they want to buy later"""

    user = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="wishlist"
    )
    item = models.ForeignKey(
        Items, on_delete=models.CASCADE, related_name="wishlisted_by"
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "item")
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user.username} - {self.item.item_name}"


# ============================================================================
# FEATURE 2: COUPON SYSTEM
# ============================================================================

class Coupon(models.Model):
    """Discount coupons/promo codes"""

    code = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=200)
    discount_percent = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    max_uses = models.IntegerField(default=100, validators=[MinValueValidator(1)])
    times_used = models.IntegerField(default=0)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    expiry_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.code} - {self.discount_percent}% off"

    def is_valid(self):
        """Check if coupon is still valid"""
        return (
            self.is_active
            and self.times_used < self.max_uses
            and timezone.now() < self.expiry_date
        )


# ============================================================================
# FEATURE 3: ORDER REVIEW
# ============================================================================

class OrderReview(models.Model):
    """Customer reviews for completed orders"""

    RATING_CHOICES = [
        (1, "⭐ Poor"),
        (2, "⭐⭐ Fair"),
        (3, "⭐⭐⭐ Good"),
        (4, "⭐⭐⭐⭐ Very Good"),
        (5, "⭐⭐⭐⭐⭐ Excellent"),
    ]

    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="review"
    )
    user = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="order_reviews"
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    review = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.order.id} - {self.rating}★"


# ============================================================================
# FEATURE 4: DAILY SPECIALS
# ============================================================================

class DailySpecial(models.Model):
    """Daily special offers"""

    item = models.ForeignKey(
        Items, on_delete=models.CASCADE, related_name="daily_specials"
    )
    date = models.DateField()
    discount_percent = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    special_price = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0)]
    )
    description = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        unique_together = ("item", "date")

    def __str__(self):
        return f"{self.item.item_name} - {self.discount_percent}% off on {self.date}"