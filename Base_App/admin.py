from django.contrib import admin
from django.utils.html import format_html
from Base_App.models import ItemList, Items, AboutUs, Feedback, BookTable, FavoriteItem, SpecialOffer, BookingNotification


# ============================================================================
# ITEM LIST (CATEGORIES) ADMIN
# ============================================================================

class ItemsInline(admin.TabularInline):
    """Inline editor for items within a category"""
    model = Items
    extra = 1
    fields = ['item_name', 'price', 'is_available', 'is_vegetarian']


class ItemListAdmin(admin.ModelAdmin):
    """Admin interface for menu categories"""
    list_display = ['category_name', 'get_items_count', 'is_active', 'display_order']
    list_filter = ['is_active', 'created_at']
    search_fields = ['category_name', 'description']
    list_editable = ['display_order', 'is_active']
    inlines = [ItemsInline]
    ordering = ['display_order']
    
    fieldsets = (
        ('Category Information', {
            'fields': ('category_name', 'description', 'display_order')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def get_items_count(self, obj):
        """Display number of items in this category"""
        count = obj.items.count()
        return format_html(
            '<span style="background-color: #17a2b8; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            count
        )
    get_items_count.short_description = 'Items Count'


# ============================================================================
# ITEMS (MENU ITEMS) ADMIN
# ============================================================================

class ItemsAdmin(admin.ModelAdmin):
    """Admin interface for menu items"""
    list_display = ['get_item_image', 'item_name', 'category', 'price', 'is_available', 'is_vegetarian', 'created_at']
    list_filter = ['category', 'is_available', 'is_vegetarian', 'is_vegan', 'is_spicy', 'created_at']
    search_fields = ['item_name', 'description', 'category__category_name']
    list_editable = ['price', 'is_available']
    readonly_fields = ['created_at', 'updated_at', 'get_image_preview']
    
    fieldsets = (
        ('Item Information', {
            'fields': ('item_name', 'description', 'category', 'price', 'preparation_time')
        }),
        ('Image', {
            'fields': ('image', 'get_image_preview')
        }),
        ('Dietary Information', {
            'fields': ('is_vegetarian', 'is_vegan', 'is_spicy')
        }),
        ('Status', {
            'fields': ('is_available',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['category', 'item_name']
    
    def get_item_image(self, obj):
        """Display thumbnail of item image"""
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 5px; object-fit: cover;" />',
                obj.image.url
            )
        return '❌ No Image'
    get_item_image.short_description = 'Image'
    
    def get_image_preview(self, obj):
        """Show full-size image preview in detail view"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; border-radius: 5px;" />',
                obj.image.url
            )
        return '❌ No image uploaded'
    get_image_preview.short_description = 'Image Preview'


# ============================================================================
# ABOUT US ADMIN
# ============================================================================

class AboutUsAdmin(admin.ModelAdmin):
    """Admin interface for About Us page"""
    fieldsets = (
        ('Description', {
            'fields': ('description',)
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'address')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Business Hours', {
            'fields': ('opening_hours',)
        }),
        ('Last Updated', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['updated_at']


# ============================================================================
# FEEDBACK (REVIEWS) ADMIN
# ============================================================================

class FeedbackAdmin(admin.ModelAdmin):
    """Admin interface for customer feedback with moderation"""
    list_display = ['user_name', 'get_rating_stars', 'email', 'get_approval_status', 'created_at']
    list_filter = ['is_approved', 'rating', 'created_at']
    search_fields = ['user_name', 'email', 'description']
    readonly_fields = ['created_at', 'updated_at', 'get_image_preview']
    actions = ['approve_feedback', 'reject_feedback']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('user_name', 'email')
        }),
        ('Review', {
            'fields': ('description', 'rating')
        }),
        ('Image', {
            'fields': ('image', 'get_image_preview')
        }),
        ('Moderation', {
            'fields': ('is_approved',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-created_at']
    
    def get_rating_stars(self, obj):
        """Display rating as stars"""
        stars = '⭐' * obj.rating
        colors = {
            1: '#dc3545',  # Red
            2: '#fd7e14',  # Orange
            3: '#ffc107',  # Yellow
            4: '#28a745',  # Green
            5: '#28a745',  # Green
        }
        return format_html(
            '<span style="color: {}; font-size: 16px;">{}</span>',
            colors.get(obj.rating, '#000'),
            stars
        )
    get_rating_stars.short_description = 'Rating'
    
    def get_approval_status(self, obj):
        """Display approval status with color"""
        if obj.is_approved:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">✓ Approved</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #ffc107; color: black; padding: 3px 10px; border-radius: 3px;">⏳ Pending</span>'
            )
    get_approval_status.short_description = 'Status'
    
    def get_image_preview(self, obj):
        """Show image preview"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; border-radius: 5px;" />',
                obj.image.url
            )
        return '❌ No image'
    get_image_preview.short_description = 'Image Preview'
    
    def approve_feedback(self, request, queryset):
        """Bulk action to approve feedback"""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'✓ {updated} feedback(s) approved.')
    approve_feedback.short_description = '✓ Approve selected feedback'
    
    def reject_feedback(self, request, queryset):
        """Bulk action to reject/delete feedback"""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'✗ {count} feedback(s) rejected.')
    reject_feedback.short_description = '✗ Reject selected feedback'


# ============================================================================
# BOOK TABLE (RESERVATIONS) ADMIN
# ============================================================================

class BookingNotificationInline(admin.TabularInline):
    """Inline view of notifications for a booking"""
    model = BookingNotification
    extra = 0
    readonly_fields = ['notification_type', 'sent_at', 'is_sent', 'error_message']
    can_delete = False


class BookTableAdmin(admin.ModelAdmin):
    """Admin interface for table bookings"""
    list_display = ['name', 'email', 'total_persons', 'booking_date', 'booking_time', 'get_status_badge', 'created_at']
    list_filter = ['status', 'booking_date', 'total_persons', 'created_at']
    search_fields = ['name', 'email', 'phone_number']
    readonly_fields = ['created_at', 'updated_at', 'confirmation_sent']
    actions = ['confirm_booking', 'cancel_booking', 'mark_completed', 'mark_no_show']
    inlines = [BookingNotificationInline]
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('name', 'email', 'phone_number')
        }),
        ('Booking Details', {
            'fields': ('total_persons', 'booking_date', 'booking_time', 'special_requests')
        }),
        ('Status & Confirmation', {
            'fields': ('status', 'confirmation_sent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-booking_date', '-booking_time']
    
    def get_status_badge(self, obj):
        """Display status with color coding"""
        colors = {
            'pending': '#ffc107',      # Yellow
            'confirmed': '#28a745',    # Green
            'cancelled': '#dc3545',    # Red
            'completed': '#17a2b8',    # Blue
            'no_show': '#6c757d',      # Gray
        }
        text_colors = {
            'pending': '#000',
            'confirmed': '#fff',
            'cancelled': '#fff',
            'completed': '#fff',
            'no_show': '#fff',
        }
        
        return format_html(
            '<span style="background-color: {}; color: {}; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#000'),
            text_colors.get(obj.status, '#fff'),
            obj.get_status_display()
        )
    get_status_badge.short_description = 'Status'
    
    def confirm_booking(self, request, queryset):
        """Bulk action to confirm bookings"""
        updated = queryset.filter(status='pending').update(status='confirmed')
        self.message_user(request, f'✓ {updated} booking(s) confirmed.')
    confirm_booking.short_description = '✓ Confirm selected bookings'
    
    def cancel_booking(self, request, queryset):
        """Bulk action to cancel bookings"""
        updated = queryset.exclude(status='completed').update(status='cancelled')
        self.message_user(request, f'✗ {updated} booking(s) cancelled.')
    cancel_booking.short_description = '✗ Cancel selected bookings'
    
    def mark_completed(self, request, queryset):
        """Bulk action to mark bookings as completed"""
        updated = queryset.update(status='completed')
        self.message_user(request, f'✓ {updated} booking(s) marked as completed.')
    mark_completed.short_description = '✓ Mark as completed'
    
    def mark_no_show(self, request, queryset):
        """Bulk action to mark bookings as no-show"""
        updated = queryset.update(status='no_show')
        self.message_user(request, f'⚠️ {updated} booking(s) marked as no-show.')
    mark_no_show.short_description = '⚠️ Mark as no-show'


# ============================================================================
# FAVORITE ITEMS ADMIN
# ============================================================================

class FavoriteItemAdmin(admin.ModelAdmin):
    """Admin interface for favorite items"""
    list_display = ['user_ip', 'item', 'added_at']
    list_filter = ['added_at', 'item__category']
    search_fields = ['user_ip', 'item__item_name']
    readonly_fields = ['added_at']
    ordering = ['-added_at']


# ============================================================================
# SPECIAL OFFERS ADMIN
# ============================================================================

class SpecialOfferAdmin(admin.ModelAdmin):
    """Admin interface for special offers"""
    list_display = ['title', 'get_discount_badge', 'get_validity_status', 'is_active', 'valid_from']
    list_filter = ['is_active', 'valid_from', 'valid_until', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'get_image_preview']
    filter_horizontal = ['applicable_items']
    
    fieldsets = (
        ('Offer Information', {
            'fields': ('title', 'description', 'discount_percentage')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Applicable Items', {
            'fields': ('applicable_items',),
            'description': 'Leave empty to apply to all items'
        }),
        ('Image', {
            'fields': ('image', 'get_image_preview')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-valid_from']
    
    def get_discount_badge(self, obj):
        """Display discount percentage"""
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">-{}%</span>',
            obj.discount_percentage
        )
    get_discount_badge.short_description = 'Discount'
    
    def get_validity_status(self, obj):
        """Display if offer is currently valid"""
        if obj.is_currently_valid():
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">✓ Active Now</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #6c757d; color: white; padding: 3px 10px; border-radius: 3px;">⏳ Not Active</span>'
            )
    get_validity_status.short_description = 'Current Status'
    
    def get_image_preview(self, obj):
        """Show image preview"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; border-radius: 5px;" />',
                obj.image.url
            )
        return '❌ No image'
    get_image_preview.short_description = 'Image Preview'


# ============================================================================
# BOOKING NOTIFICATIONS ADMIN
# ============================================================================

class BookingNotificationAdmin(admin.ModelAdmin):
    """Admin interface for booking notifications"""
    list_display = ['booking', 'notification_type', 'get_sent_status', 'sent_at']
    list_filter = ['notification_type', 'is_sent', 'sent_at']
    search_fields = ['booking__name', 'booking__email']
    readonly_fields = ['sent_at', 'booking', 'notification_type', 'is_sent', 'error_message']
    
    def has_add_permission(self, request):
        return False  # Don't allow manual creation
    
    def has_delete_permission(self, request, obj=None):
        return False  # Don't allow deletion
    
    def get_sent_status(self, obj):
        """Display if notification was sent"""
        if obj.is_sent:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">✓ Sent</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">✗ Failed</span>'
            )
    get_sent_status.short_description = 'Status'


# ============================================================================
# ADMIN SITE CUSTOMIZATION
# ============================================================================

admin.site.site_header = "🍽️ Feane Restaurant Admin"
admin.site.site_title = "Feane Admin"
admin.site.index_title = "Welcome to Feane Admin Panel"


# ============================================================================
# REGISTER MODELS
# ============================================================================

admin.site.register(ItemList, ItemListAdmin)
admin.site.register(Items, ItemsAdmin)
admin.site.register(AboutUs, AboutUsAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(BookTable, BookTableAdmin)
admin.site.register(FavoriteItem, FavoriteItemAdmin)
admin.site.register(SpecialOffer, SpecialOfferAdmin)
admin.site.register(BookingNotification, BookingNotificationAdmin)