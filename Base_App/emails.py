# Base_App/emails.py
# Simple email utility functions - Plain text version (NO templates needed!)

from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# ORDER CONFIRMATION EMAIL
# ============================================================================

def send_order_confirmation_email(order):
    """Send order confirmation email to customer (Plain Text)"""
    try:
        subject = f"🎉 Order Confirmation #{order.id} - Feane"
        
        # Build email body
        items_text = ""
        for item in order.items.all():
            items_text += f"\n• {item.item.item_name} x {item.quantity} = ${item.subtotal}"
        
        message = f"""
Hi {order.customer_name},

Thank you for your order! We're excited to prepare your delicious meal.

📋 ORDER DETAILS
=====================================
Order ID: #{order.id}
Order Date: {order.created_at.strftime('%B %d, %Y at %I:%M %p')}
Status: ⏳ Pending Confirmation
Delivery Type: {'🚗 Home Delivery' if order.delivery_type == 'delivery' else '🏪 Pickup'}

🍽️ YOUR ITEMS
=====================================
{items_text}

💰 PRICE SUMMARY
=====================================
Subtotal: ${order.total_amount}
Delivery Charge: FREE
Tax & Fees: $0.00
---
TOTAL: ${order.total_amount}

📍 DELIVERY ADDRESS
=====================================
{order.delivery_address}
{order.delivery_city} - {order.delivery_pincode}

{'📝 SPECIAL REQUESTS' + chr(10) + '=====================================' + chr(10) + order.special_requests + chr(10) if order.special_requests else ''}

⏭️ WHAT'S NEXT?
=====================================
✓ We'll confirm your order within a few minutes
✓ Our team will start preparing your food
✓ You'll receive updates via email as your order progresses
✓ Estimated delivery time: 30 minutes

📞 NEED HELP?
=====================================
Call us: +91 9876543210
Email: support@feanefoods.com

---

Thank you for choosing Feane! Enjoy your delicious meal! 🍕

This is an automated message. Please don't reply to this email.
© 2024 Feane Restaurant. All rights reserved.
"""
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            fail_silently=False,
        )
        
        logger.info(f"Order confirmation email sent to {order.customer_email} for order #{order.id}")
        return True
    
    except Exception as e:
        logger.error(f"Error sending order confirmation email: {str(e)}")
        return False


# ============================================================================
# ORDER STATUS UPDATE EMAIL
# ============================================================================

def send_order_status_email(order, old_status, new_status):
    """Send order status update email to customer (Plain Text)"""
    try:
        status_messages = {
            'pending': '⏳ Your order is pending confirmation',
            'confirmed': '✓ Your order has been confirmed!',
            'preparing': '🍳 We are preparing your delicious food',
            'ready': '✓ Your order is ready for pickup/delivery',
            'delivered': '🎉 Your order has been delivered!',
            'cancelled': '❌ Your order has been cancelled',
        }
        
        subject = f"📦 Order Update - {status_messages.get(new_status, 'Status Updated')} #{order.id}"
        
        message = f"""
Hi {order.customer_name},

Great news! Your order has been updated.

📦 CURRENT STATUS: {status_messages.get(new_status, 'Status Updated')}

📋 ORDER INFORMATION
=====================================
Order ID: #{order.id}
Current Status: {new_status.upper()}
Delivery Type: {'🚗 Home Delivery' if order.delivery_type == 'delivery' else '🏪 Pickup'}
Total Amount: ${order.total_amount}

📍 DELIVERY ADDRESS
=====================================
{order.delivery_address}
{order.delivery_city} - {order.delivery_pincode}

📞 QUESTIONS?
=====================================
Call us: +91 9876543210
Email: support@feanefoods.com

---

We appreciate your order! 🍕

This is an automated message. Please don't reply to this email.
© 2024 Feane Restaurant. All rights reserved.
"""
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.customer_email],
            fail_silently=False,
        )
        
        logger.info(f"Order status email sent to {order.customer_email} for order #{order.id} ({old_status} -> {new_status})")
        return True
    
    except Exception as e:
        logger.error(f"Error sending order status email: {str(e)}")
        return False


# ============================================================================
# BOOKING CONFIRMATION EMAIL
# ============================================================================

def send_booking_confirmation_email(booking):
    """Send table booking confirmation email"""
    try:
        subject = f"🎉 Booking Confirmation #{booking.id} - Feane"
        
        message = f"""
Hi {booking.name},

Thank you for booking a table at Feane! We're excited to have you.

📋 YOUR BOOKING DETAILS
=====================================
Booking ID: #{booking.id}
Name: {booking.name}
Phone: {booking.phone_number}
Email: {booking.email}
Date: {booking.booking_date.strftime('%A, %B %d, %Y')}
Time: {booking.booking_time.strftime('%I:%M %p')}
Persons: {booking.total_persons}

{'📝 SPECIAL REQUESTS' + chr(10) + '=====================================' + chr(10) + booking.special_requests + chr(10) if booking.special_requests else ''}

📍 LOCATION
=====================================
Koramangala, Bangalore
📞 Call us: +91 9876543210

⏰ IMPORTANT
=====================================
• Please arrive 10 minutes before your reservation
• If you need to cancel or modify, contact us ASAP
• Reservations are held for 15 minutes

Looking forward to serving you amazing food!

---

Best regards,
Feane Restaurant Team 🍽️

This is an automated message. Please don't reply to this email.
© 2024 Feane Restaurant. All rights reserved.
"""
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.email],
            fail_silently=False,
        )
        
        logger.info(f"Booking confirmation email sent to {booking.email} for booking #{booking.id}")
        return True
    
    except Exception as e:
        logger.error(f"Error sending booking confirmation email: {str(e)}")
        return False


# ============================================================================
# FEEDBACK RECEIVED EMAIL
# ============================================================================

def send_feedback_received_email(feedback):
    """Send feedback acknowledgment email"""
    try:
        subject = "📝 Thank You for Your Feedback - Feane"
        
        message = f"""
Hi {feedback.user_name},

Thank you so much for taking the time to share your feedback with us!

We really appreciate your thoughts and suggestions. Your feedback helps us improve our service and ensure that every customer has a great experience at Feane.

⭐ Rating: {feedback.rating}/5 Stars
💬 Your Feedback: {feedback.description}

Your review will be published on our website after moderation.

If you have any other feedback or questions, feel free to reach out to us anytime!

📞 CONTACT US
=====================================
Call: +91 9876543210
Email: support@feanefoods.com

---

Thank you for choosing Feane! 🍕

Best regards,
Feane Restaurant Team

This is an automated message. Please don't reply to this email.
© 2024 Feane Restaurant. All rights reserved.
"""
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[feedback.email],
            fail_silently=False,
        )
        
        logger.info(f"Feedback received email sent to {feedback.email}")
        return True
    
    except Exception as e:
        logger.error(f"Error sending feedback received email: {str(e)}")
        return False


# ============================================================================
# ADMIN NOTIFICATION EMAILS
# ============================================================================

def send_admin_new_order_notification(order):
    """Send new order notification to admin"""
    try:
        subject = f"🔔 New Order #{order.id} Received - Feane Admin"
        
        items_text = ""
        for item in order.items.all():
            items_text += f"\n• {item.item.item_name} x {item.quantity} = ${item.subtotal}"
        
        message = f"""
ADMIN NOTIFICATION - NEW ORDER RECEIVED

Order ID: #{order.id}
Customer Name: {order.customer_name}
Customer Email: {order.customer_email}
Customer Phone: {order.customer_phone}

Items Ordered:{items_text}

Total Amount: ${order.total_amount}
Delivery Type: {'Home Delivery' if order.delivery_type == 'delivery' else 'Pickup'}
Delivery Address: {order.delivery_address}, {order.delivery_city}

{'Special Requests: ' + order.special_requests if order.special_requests else 'No special requests'}

Please log in to the admin panel to confirm and manage this order.

---
This is an automated admin notification.
"""
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        
        logger.info(f"Admin notification sent for new order #{order.id}")
        return True
    
    except Exception as e:
        logger.error(f"Error sending admin notification: {str(e)}")
        return False


def send_admin_new_feedback_notification(feedback):
    """Send new feedback notification to admin"""
    try:
        subject = f"🔔 New Feedback Received - Feane Admin"
        
        message = f"""
ADMIN NOTIFICATION - NEW FEEDBACK RECEIVED

Customer Name: {feedback.user_name}
Customer Email: {feedback.email}
Rating: {feedback.rating}/5 Stars

Feedback:
{feedback.description}

Please log in to the admin panel to review and approve this feedback.

---
This is an automated admin notification.
"""
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        
        logger.info(f"Admin notification sent for new feedback from {feedback.user_name}")
        return True
    
    except Exception as e:
        logger.error(f"Error sending admin feedback notification: {str(e)}")
        return False