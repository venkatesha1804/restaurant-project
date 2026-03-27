# Base_App/views.py - COPY THIS ENTIRE FILE AND REPLACE YOUR views.py

from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from Base_App.models import Cart, Order, OrderItem, Items, BookTable, AboutUs, Feedback, ItemList, FavoriteItem, SpecialOffer
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Prefetch, Avg
from django.http import JsonResponse
import logging

from Base_App.forms import BookTableForm, FeedbackForm, ContactForm

logger = logging.getLogger(__name__)


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

@require_http_methods(["GET", "POST"])
def LoginView(request):
    """Handle user login with proper authentication"""
    if request.user.is_authenticated:
        return redirect('Home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'✓ Welcome back, {username}!')
                logger.info(f"User {username} logged in successfully at {timezone.now()}")
                
                next_page = request.GET.get('next', 'Home')
                return redirect(next_page)
            else:
                messages.error(request, '✗ Invalid credentials. Please try again.')
                logger.warning(f"Failed login attempt for username: {username} at {timezone.now()}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            logger.warning(f"Login form validation failed: {form.errors}")
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})


@require_http_methods(["GET", "POST"])
def SignupView(request):
    """Handle user registration with proper validation"""
    if request.user.is_authenticated:
        return redirect('Home')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        
        if form.is_valid():
            try:
                user = form.save()
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, f'✓ Account created successfully! Welcome, {username}!')
                    logger.info(f"New user registered: {username} at {timezone.now()}")
                    return redirect('Home')
                else:
                    messages.warning(request, 'Account created but login failed. Please login manually.')
                    return redirect('login')
                    
            except Exception as e:
                logger.error(f"Error during signup: {str(e)}")
                messages.error(request, f'Error creating account: {str(e)}')
                return render(request, 'login.html', {'form': form})
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            logger.warning(f"Signup form validation failed: {form.errors}")
    else:
        form = UserCreationForm()
    
    return render(request, 'login.html', {'form': form})


@require_http_methods(["POST"])
def LogoutView(request):
    """Handle user logout"""
    username = request.user.username if request.user.is_authenticated else "Unknown"
    logout(request)
    messages.success(request, '✓ You have been logged out successfully.')
    logger.info(f"User {username} logged out at {timezone.now()}")
    return redirect('Home')


# ============================================================================
# MAIN PAGES
# ============================================================================

def HomeView(request):
    """Home page with featured items, special offers, and customer reviews"""
    try:
        categories = ItemList.objects.filter(is_active=True).prefetch_related(
            Prefetch('items', queryset=Items.objects.filter(is_available=True))
        ).order_by('display_order')
        
        reviews = Feedback.objects.filter(is_approved=True).select_related().order_by('-created_at')[:5]
        
        now = timezone.now()
        special_offers = SpecialOffer.objects.filter(
            is_active=True,
            valid_from__lte=now,
            valid_until__gte=now
        ).order_by('-valid_from')[:2]

        avg_rating = Feedback.objects.filter(is_approved=True).aggregate(
            avg=Avg('rating')
        )['avg'] or 0

        context = {
            'categories': categories,
            'reviews': reviews,
            'special_offers': special_offers,
            'avg_rating': round(avg_rating, 1),
        }
        return render(request, 'home.html', context)
    
    except Exception as e:
        logger.error(f"Error in HomeView: {str(e)}")
        messages.error(request, '✗ Unable to load home page. Please try again.')
        return render(request, 'home.html', {'error': 'Unable to load content'})


def AboutView(request):
    """About us page with restaurant information"""
    try:
        about_data = AboutUs.objects.first()
        return render(request, 'about.html', {'data': about_data})
    except Exception as e:
        logger.error(f"Error in AboutView: {str(e)}")
        messages.error(request, '✗ Unable to load information.')
        return render(request, 'about.html', {'error': 'Unable to load information'})


def MenuView(request):
    """Menu page with category filtering and search"""
    try:
        categories = ItemList.objects.filter(is_active=True).prefetch_related(
            Prefetch('items', queryset=Items.objects.filter(is_available=True))
        ).order_by('display_order')
        
        items = Items.objects.filter(is_available=True).select_related('category')
        
        category_id = request.GET.get('category')
        if category_id:
            try:
                items = items.filter(category_id=int(category_id))
            except (ValueError, TypeError):
                pass

        search_query = request.GET.get('q')
        if search_query:
            items = items.filter(
                Q(item_name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )

        context = {
            'list': categories,
            'items': items,
            'selected_category': category_id,
            'search_query': search_query,
        }
        return render(request, 'menu.html', context)
    
    except Exception as e:
        logger.error(f"Error in MenuView: {str(e)}")
        messages.error(request, '✗ Unable to load menu.')
        return render(request, 'menu.html', {'error': 'Unable to load menu'})


# ============================================================================
# BOOKING & FEEDBACK
# ============================================================================

@require_http_methods(["GET", "POST"])
def BookTableView(request):
    """Handle table booking with comprehensive validation"""
    if request.method == 'POST':
        form = BookTableForm(request.POST)
        
        if form.is_valid():
            try:
                booking = form.save(commit=False)
                booking.status = 'pending'
                booking.save()
                
                send_booking_confirmation_email(booking)
                booking.confirmation_sent = True
                booking.save()
                
                logger.info(
                    f"Booking created: ID={booking.id}, "
                    f"Name={booking.name}, "
                    f"Date={booking.booking_date}, "
                    f"Time={booking.booking_time}"
                )
                
                messages.success(
                    request,
                    f'✓ Table booked successfully for {booking.total_persons} person(s) '
                    f'on {booking.booking_date.strftime("%B %d, %Y")} at '
                    f'{booking.booking_time.strftime("%I:%M %p")}! '
                    'Check your email for confirmation.'
                )
                
            except Exception as e:
                logger.error(f"Error processing booking: {str(e)}")
                messages.error(request, f'✗ Error processing your booking: {str(e)}')
                return render(request, 'book_table.html', {'form': form})
            
            return redirect('Book_Table')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, f"✗ {error}")
                    else:
                        messages.error(request, f"✗ {field.upper()}: {error}")
            logger.warning(f"BookTable form validation failed: {form.errors}")
    
    else:
        form = BookTableForm()
    
    return render(request, 'book_table.html', {'form': form})


def send_booking_confirmation_email(booking):
    """Send professional booking confirmation email to customer"""
    try:
        subject = f'🎉 Booking Confirmation - {booking.name}'
        
        message = f'''
Hello {booking.name},

Thank you for booking a table at Feane! We're excited to have you.

📋 YOUR BOOKING DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Booking ID: {booking.id}
Name: {booking.name}
Phone: {booking.phone_number}
Email: {booking.email}
Date: {booking.booking_date.strftime('%A, %B %d, %Y')}
Time: {booking.booking_time.strftime('%I:%M %p')}
Persons: {booking.total_persons}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{f"Special Requests: {booking.special_requests}" if booking.special_requests else ""}

📍 LOCATION
Koramangala, Bangalore
📞 Call us: +91 9876543210

⏰ IMPORTANT
- Please arrive 10 minutes before your reservation
- If you need to cancel or modify, contact us ASAP
- Reservations are held for 15 minutes

Looking forward to serving you amazing food!

Best regards,
Feane Restaurant Team
🍽️ Delicious Experience Awaits

---
This is an automated message. Please don't reply to this email.
'''
        
        send_mail(
            subject,
            message,
            'support@feanefoods.com',
            [booking.email],
            fail_silently=False,
        )
        logger.info(f"Confirmation email sent to {booking.email} for booking {booking.id}")
    
    except Exception as e:
        logger.error(f"Email sending failed for booking {booking.id}: {str(e)}")


@require_http_methods(["GET", "POST"])
def FeedbackView(request):
    """Handle customer feedback and reviews with moderation"""
    if request.method == 'POST':
        form = FeedbackForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                feedback = form.save(commit=False)
                feedback.is_approved = False
                feedback.save()
                
                logger.info(
                    f"Feedback received from {feedback.user_name} "
                    f"with rating {feedback.rating} stars"
                )
                
                messages.success(
                    request,
                    '✓ Thank you for your feedback! '
                    'Your review will be published after moderation. '
                    'We appreciate your time!'
                )
                
            except Exception as e:
                logger.error(f"Error saving feedback: {str(e)}")
                messages.error(request, f'✗ Error submitting feedback: {str(e)}')
                return render(request, 'feedback.html', {'form': form})
            
            return redirect('Feedback_Form')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, f"✗ {error}")
                    else:
                        messages.error(request, f"✗ {field.upper()}: {error}")
            logger.warning(f"Feedback form validation failed: {form.errors}")
    
    else:
        form = FeedbackForm()
    
    approved_feedbacks = Feedback.objects.filter(is_approved=True).order_by('-created_at')[:10]
    
    context = {
        'form': form,
        'feedbacks': approved_feedbacks,
    }
    
    return render(request, 'feedback.html', context)


@require_http_methods(["POST"])
def add_to_favorites(request, item_id):
    """Add item to favorites (AJAX endpoint)"""
    try:
        user_ip = get_client_ip(request)
        item = Items.objects.get(id=item_id)
        
        favorite, created = FavoriteItem.objects.get_or_create(
            user_ip=user_ip,
            item=item
        )
        
        if created:
            logger.info(f"Item {item.item_name} added to favorites from IP {user_ip}")
            return JsonResponse({
                'success': True,
                'message': f'✓ {item.item_name} added to favorites!'
            })
        else:
            favorite.delete()
            logger.info(f"Item {item.item_name} removed from favorites from IP {user_ip}")
            return JsonResponse({
                'success': True,
                'message': f'✗ {item.item_name} removed from favorites'
            })
    
    except Items.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Item not found'}, status=404)
    except Exception as e:
        logger.error(f"Error adding to favorites: {str(e)}")
        return JsonResponse({'success': False, 'message': 'Error adding to favorites'}, status=500)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# ============================================================================
# ADMIN DASHBOARD
# ============================================================================

@login_required(login_url='login')
def admin_dashboard(request):
    """Professional admin dashboard with analytics"""
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, '✗ You do not have permission to access the admin dashboard.')
        logger.warning(f"Unauthorized admin access attempt by user {request.user.username}")
        return redirect('Home')
    
    try:
        total_items = Items.objects.filter(is_available=True).count()
        total_categories = ItemList.objects.filter(is_active=True).count()
        
        recent_bookings = BookTable.objects.all().order_by('-created_at')[:10]
        pending_bookings = BookTable.objects.filter(status='pending').count()
        confirmed_bookings = BookTable.objects.filter(status='confirmed').count()
        completed_bookings = BookTable.objects.filter(status='completed').count()
        
        today = timezone.now().date()
        next_week = today + timezone.timedelta(days=7)
        upcoming_bookings = BookTable.objects.filter(
            booking_date__range=[today, next_week],
            status__in=['pending', 'confirmed']
        ).order_by('booking_date', 'booking_time')
        
        approved_feedbacks = Feedback.objects.filter(is_approved=True).order_by('-created_at')[:5]
        pending_feedbacks = Feedback.objects.filter(is_approved=False).count()
        
        avg_rating = Feedback.objects.filter(is_approved=True).aggregate(
            avg=Avg('rating')
        )['avg'] or 0

        now = timezone.now()
        active_offers = SpecialOffer.objects.filter(
            is_active=True,
            valid_from__lte=now,
            valid_until__gte=now
        )

        context = {
            'total_items': total_items,
            'total_categories': total_categories,
            'recent_bookings': recent_bookings,
            'pending_bookings': pending_bookings,
            'confirmed_bookings': confirmed_bookings,
            'completed_bookings': completed_bookings,
            'upcoming_bookings': upcoming_bookings,
            'approved_feedbacks': approved_feedbacks,
            'pending_feedbacks': pending_feedbacks,
            'avg_rating': round(avg_rating, 1),
            'active_offers': active_offers,
        }
        
        logger.info(f"Admin dashboard accessed by {request.user.username}")
        return render(request, 'admin_dashboard.html', context)
    
    except Exception as e:
        logger.error(f"Error in admin_dashboard: {str(e)}")
        messages.error(request, '✗ Error loading dashboard')
        return render(request, 'admin_dashboard.html', {'error': 'Unable to load data'})


# ============================================================================
# CONTACT FORM
# ============================================================================

@require_http_methods(["GET", "POST"])
def contact_view(request):
    """Handle contact form submissions"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        
        if form.is_valid():
            try:
                name = form.cleaned_data.get('name')
                email = form.cleaned_data.get('email')
                phone = form.cleaned_data.get('phone')
                subject = form.cleaned_data.get('subject')
                message_text = form.cleaned_data.get('message')
                
                send_mail(
                    f"New Contact Form: {subject}",
                    f"From: {name} ({email})\nPhone: {phone}\n\n{message_text}",
                    'support@feanefoods.com',
                    ['admin@feanefoods.com'],
                    fail_silently=False,
                )
                
                logger.info(f"Contact form submitted by {name} ({email})")
                messages.success(request, '✓ Thank you! We will respond to you soon.')
                return redirect('contact')
                
            except Exception as e:
                logger.error(f"Error sending contact email: {str(e)}")
                messages.error(request, '✗ Error sending your message. Please try again.')
                return render(request, 'contact.html', {'form': form})
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"✗ {field.upper()}: {error}")
    
    else:
        form = ContactForm()
    
    return render(request, 'contact.html', {'form': form})


# ============================================================================
# CART MANAGEMENT VIEWS
# ============================================================================

def get_or_create_cart(request):
    """Get or create cart for user/session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    
    return cart


@require_http_methods(["POST"])
def add_to_cart(request, item_id):
    """Add item to cart via AJAX"""
    try:
        item = get_object_or_404(Items, id=item_id, is_available=True)
        cart = get_or_create_cart(request)
        
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            item=item
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
            message = f'✓ Updated {item.item_name} quantity in cart!'
        else:
            cart_item.quantity = quantity
            cart_item.save()
            message = f'✓ {item.item_name} added to cart!'
        
        logger.info(f"Item {item.item_name} added to cart")
        
        return JsonResponse({
            'success': True,
            'message': message,
            'cart_count': cart.get_total_quantity(),
            'total_price': float(cart.get_total_price())
        })
    
    except Items.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Item not found'
        }, status=404)
    
    except Exception as e:
        logger.error(f"Error adding to cart: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error adding to cart'
        }, status=500)


@require_http_methods(["GET"])
def view_cart(request):
    """View shopping cart page"""
    try:
        cart = get_or_create_cart(request)
        cart_items = cart.items.all()
        total_price = cart.get_total_price()
        total_items = cart.get_total_items()
        
        context = {
            'cart': cart,
            'cart_items': cart_items,
            'total_price': total_price,
            'total_items': total_items,
        }
        
        return render(request, 'cart.html', context)
    
    except Exception as e:
        logger.error(f"Error viewing cart: {str(e)}")
        messages.error(request, 'Error loading cart')
        return redirect('Menu')


@require_http_methods(["POST"])
def update_cart_item(request, item_id):
    """Update quantity of item in cart"""
    try:
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, cart=cart, item_id=item_id)
        
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity < 1:
            cart_item.delete()
            message = f'✓ Item removed from cart'
        else:
            cart_item.quantity = quantity
            cart_item.save()
            message = f'✓ Quantity updated'
        
        logger.info(f"Cart item {item_id} updated")
        
        return JsonResponse({
            'success': True,
            'message': message,
            'cart_count': cart.get_total_quantity(),
            'total_price': float(cart.get_total_price()),
            'subtotal': float(cart_item.get_subtotal()) if quantity > 0 else 0
        })
    
    except CartItem.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Item not in cart'
        }, status=404)
    
    except Exception as e:
        logger.error(f"Error updating cart: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error updating cart'
        }, status=500)


@require_http_methods(["POST"])
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    try:
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, cart=cart, item_id=item_id)
        
        item_name = cart_item.item.item_name
        cart_item.delete()
        
        logger.info(f"Item {item_id} removed from cart")
        
        return JsonResponse({
            'success': True,
            'message': f'✓ {item_name} removed from cart',
            'cart_count': cart.get_total_quantity(),
            'total_price': float(cart.get_total_price())
        })
    
    except CartItem.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Item not in cart'
        }, status=404)
    
    except Exception as e:
        logger.error(f"Error removing from cart: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error removing item'
        }, status=500)


@require_http_methods(["POST"])
def clear_cart(request):
    """Clear entire cart"""
    try:
        cart = get_or_create_cart(request)
        cart.clear_cart()
        
        logger.info("Cart cleared")
        
        return JsonResponse({
            'success': True,
            'message': '✓ Cart cleared',
            'cart_count': 0,
            'total_price': 0
        })
    
    except Exception as e:
        logger.error(f"Error clearing cart: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error clearing cart'
        }, status=500)


@require_http_methods(["GET"])
def get_cart_count(request):
    """Get cart item count (for AJAX)"""
    try:
        cart = get_or_create_cart(request)
        return JsonResponse({
            'cart_count': cart.get_total_quantity(),
            'total_price': float(cart.get_total_price())
        })
    
    except Exception as e:
        logger.error(f"Error getting cart count: {str(e)}")
        return JsonResponse({
            'cart_count': 0,
            'total_price': 0
        })


# ============================================================================
# CHECKOUT & ORDER VIEWS
# ============================================================================

@require_http_methods(["GET", "POST"])
def checkout(request):
    """Checkout page - customer enters delivery details"""
    try:
        if request.user.is_authenticated:
            cart = get_object_or_404(Cart, user=request.user)
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            cart = get_object_or_404(Cart, session_key=session_key)
        
        if not cart.items.exists():
            messages.error(request, '✗ Your cart is empty')
            return redirect('view_cart')
        
        if request.method == 'POST':
            customer_name = request.POST.get('customer_name')
            customer_email = request.POST.get('customer_email')
            customer_phone = request.POST.get('customer_phone')
            delivery_type = request.POST.get('delivery_type', 'delivery')
            delivery_address = request.POST.get('delivery_address')
            delivery_city = request.POST.get('delivery_city', 'Bangalore')
            delivery_pincode = request.POST.get('delivery_pincode')
            special_requests = request.POST.get('special_requests', '')
            
            if not all([customer_name, customer_email, customer_phone, delivery_address, delivery_pincode]):
                messages.error(request, '✗ Please fill all required fields')
                return render(request, 'checkout.html', {
                    'cart': cart,
                    'cart_items': cart.items.all(),
                    'total_price': cart.get_total_price(),
                    'total_items': cart.get_total_items(),
                })
            
            try:
                order = Order.objects.create(
                    customer_name=customer_name,
                    customer_email=customer_email,
                    customer_phone=customer_phone,
                    delivery_type=delivery_type,
                    delivery_address=delivery_address,
                    delivery_city=delivery_city,
                    delivery_pincode=delivery_pincode,
                    special_requests=special_requests,
                    total_amount=cart.get_total_price(),
                    status='pending',
                    payment_status='pending'
                )
                
                for cart_item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        item=cart_item.item,
                        quantity=cart_item.quantity,
                        price_at_purchase=cart_item.item.price,
                        subtotal=cart_item.get_subtotal()
                    )
                
                # SEND CONFIRMATION EMAIL
                from Base_App.emails import send_order_confirmation_email
                send_order_confirmation_email(order)
                
                logger.info(f"Order created: #{order.id} by {customer_name}")
                
                cart.clear_cart()
                
                return redirect('order_confirmation', order_id=order.id)
            
            except Exception as e:
                logger.error(f"Error creating order: {str(e)}")
                messages.error(request, f'✗ Error creating order: {str(e)}')
        
        context = {
            'cart': cart,
            'cart_items': cart.items.all(),
            'total_price': cart.get_total_price(),
            'total_items': cart.get_total_items(),
            'user': request.user if request.user.is_authenticated else None,
        }
        
        return render(request, 'checkout.html', context)
    
    except Cart.DoesNotExist:
        messages.error(request, '✗ Cart not found')
        return redirect('view_cart')
    
    except Exception as e:
        logger.error(f"Error in checkout: {str(e)}")
        messages.error(request, '✗ Error processing checkout')
        return redirect('view_cart')


@require_http_methods(["GET"])
def order_confirmation(request, order_id):
    """Order confirmation page"""
    try:
        order = get_object_or_404(Order, id=order_id)
        
        context = {
            'order': order,
            'order_items': order.items.all(),
            'total_items': order.get_total_items(),
        }
        
        logger.info(f"Order confirmation viewed: #{order.id}")
        return render(request, 'order_confirmation.html', context)
    
    except Exception as e:
        logger.error(f"Error in order confirmation: {str(e)}")
        messages.error(request, '✗ Order not found')
        return redirect('Home')


@require_http_methods(["GET"])
def order_history(request):
    """View customer's order history"""
    try:
        if request.user.is_authenticated:
            orders = Order.objects.filter(
                customer_email=request.user.email
            ).order_by('-created_at')
        else:
            messages.error(request, '✗ Please login to view order history')
            return redirect('login')
        
        context = {
            'orders': orders,
        }
        
        return render(request, 'order_history.html', context)
    
    except Exception as e:
        logger.error(f"Error in order history: {str(e)}")
        messages.error(request, '✗ Error loading order history')
        return redirect('Home')


@require_http_methods(["GET"])
def order_detail(request, order_id):
    """View single order details"""
    try:
        order = get_object_or_404(Order, id=order_id)
        
        if request.user.is_authenticated:
            if order.customer_email != request.user.email:
                messages.error(request, '✗ You do not have permission to view this order')
                return redirect('order_history')
        else:
            messages.error(request, '✗ Please login to view order details')
            return redirect('login')
        
        context = {
            'order': order,
            'order_items': order.items.all(),
            'total_items': order.get_total_items(),
        }
        
        return render(request, 'order_detail.html', context)
    
    except Exception as e:
        logger.error(f"Error in order detail: {str(e)}")
        messages.error(request, '✗ Order not found')
        return redirect('order_history')


@require_http_methods(["POST"])
def update_order_status(request, order_id):
    """Admin endpoint to update order status"""
    try:
        if not request.user.is_staff and not request.user.is_superuser:
            return JsonResponse({
                'success': False,
                'message': 'Permission denied'
            }, status=403)
        
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        if new_status not in dict(Order.ORDER_STATUS_CHOICES):
            return JsonResponse({
                'success': False,
                'message': 'Invalid status'
            }, status=400)
        
        order.status = new_status
        order.save()
        
        logger.info(f"Order #{order.id} status updated to {new_status}")
        
        return JsonResponse({
            'success': True,
            'message': f'Order status updated to {new_status}',
            'status': new_status,
        })
    
    except Order.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Order not found'
        }, status=404)
    
    except Exception as e:
        logger.error(f"Error updating order status: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error updating order'
        }, status=500)


# ============================================================================
# ADMIN ORDER MANAGEMENT VIEWS
# ============================================================================

def admin_required(user):
    """Check if user is admin/staff"""
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(admin_required)
@require_http_methods(["GET"])
def admin_orders(request):
    """Admin order management dashboard"""
    try:
        status_filter = request.GET.get('status', 'all')
        search_query = request.GET.get('search', '')
        
        orders = Order.objects.all().order_by('-created_at')
        
        if status_filter != 'all':
            orders = orders.filter(status=status_filter)
        
        if search_query:
            orders = orders.filter(
                Q(customer_name__icontains=search_query) |
                Q(customer_phone__icontains=search_query) |
                Q(customer_email__icontains=search_query)
            )
        
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        confirmed_orders = Order.objects.filter(status='confirmed').count()
        preparing_orders = Order.objects.filter(status='preparing').count()
        ready_orders = Order.objects.filter(status='ready').count()
        delivered_orders = Order.objects.filter(status='delivered').count()
        
        total_revenue = Order.objects.filter(status='delivered').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        today_revenue = Order.objects.filter(
            created_at__date=timezone.now().date(),
            status='delivered'
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        page = request.GET.get('page', 1)
        from django.core.paginator import Paginator
        paginator = Paginator(orders, 10)
        orders_page = paginator.get_page(page)
        
        context = {
            'orders': orders_page,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'confirmed_orders': confirmed_orders,
            'preparing_orders': preparing_orders,
            'ready_orders': ready_orders,
            'delivered_orders': delivered_orders,
            'total_revenue': float(total_revenue),
            'today_revenue': float(today_revenue),
            'status_filter': status_filter,
            'search_query': search_query,
            'statuses': [
                ('pending', '⏳ Pending'),
                ('confirmed', '✓ Confirmed'),
                ('preparing', '🍳 Preparing'),
                ('ready', '✓ Ready'),
                ('delivered', '✓ Delivered'),
                ('cancelled', '✗ Cancelled'),
            ]
        }
        
        logger.info(f"Admin accessed orders dashboard - Total: {total_orders}")
        return render(request, 'admin_orders.html', context)
    
    except Exception as e:
        logger.error(f"Error in admin_orders: {str(e)}")
        messages.error(request, '✗ Error loading orders')
        return redirect('admin_dashboard')


@login_required
@user_passes_test(admin_required)
@require_http_methods(["GET"])
def admin_order_detail(request, order_id):
    """Admin view single order details"""
    try:
        order = get_object_or_404(Order, id=order_id)
        order_items = order.items.all()
        
        context = {
            'order': order,
            'order_items': order_items,
            'total_items': order.get_total_items(),
            'statuses': [
                ('pending', '⏳ Pending'),
                ('confirmed', '✓ Confirmed'),
                ('preparing', '🍳 Preparing'),
                ('ready', '✓ Ready'),
                ('delivered', '✓ Delivered'),
                ('cancelled', '✗ Cancelled'),
            ]
        }
        
        logger.info(f"Admin viewed order #{order.id}")
        return render(request, 'admin_order_detail.html', context)
    
    except Exception as e:
        logger.error(f"Error in admin_order_detail: {str(e)}")
        messages.error(request, '✗ Order not found')
        return redirect('admin_orders')


@login_required
@user_passes_test(admin_required)
@require_http_methods(["POST"])
def admin_update_order_status(request, order_id):
    """Update order status via AJAX"""
    try:
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        valid_statuses = ['pending', 'confirmed', 'preparing', 'ready', 'delivered', 'cancelled']
        if new_status not in valid_statuses:
            return JsonResponse({
                'success': False,
                'message': 'Invalid status'
            }, status=400)
        
        old_status = order.status
        order.status = new_status
        order.save()
        
        logger.info(f"Order #{order.id} status updated from {old_status} to {new_status} by {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'message': f'✓ Order status updated to {new_status}',
            'status': new_status,
            'status_label': dict([
                ('pending', '⏳ Pending'),
                ('confirmed', '✓ Confirmed'),
                ('preparing', '🍳 Preparing'),
                ('ready', '✓ Ready'),
                ('delivered', '✓ Delivered'),
                ('cancelled', '✗ Cancelled'),
            ]).get(new_status, new_status)
        })
    
    except Order.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Order not found'
        }, status=404)
    
    except Exception as e:
        logger.error(f"Error updating order status: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error updating order'
        }, status=500)


@login_required
@user_passes_test(admin_required)
@require_http_methods(["GET"])
def admin_order_stats(request):
    """Get order statistics for dashboard"""
    try:
        today = timezone.now().date()
        today_orders = Order.objects.filter(created_at__date=today)
        today_count = today_orders.count()
        today_revenue = today_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        week_start = today - timedelta(days=today.weekday())
        week_orders = Order.objects.filter(created_at__date__gte=week_start)
        week_count = week_orders.count()
        week_revenue = week_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        month_start = today.replace(day=1)
        month_orders = Order.objects.filter(created_at__date__gte=month_start)
        month_count = month_orders.count()
        month_revenue = month_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        status_breakdown = {
            'pending': Order.objects.filter(status='pending').count(),
            'confirmed': Order.objects.filter(status='confirmed').count(),
            'preparing': Order.objects.filter(status='preparing').count(),
            'ready': Order.objects.filter(status='ready').count(),
            'delivered': Order.objects.filter(status='delivered').count(),
        }
        
        return JsonResponse({
            'success': True,
            'today': {
                'count': today_count,
                'revenue': float(today_revenue)
            },
            'week': {
                'count': week_count,
                'revenue': float(week_revenue)
            },
            'month': {
                'count': month_count,
                'revenue': float(month_revenue)
            },
            'status_breakdown': status_breakdown
        })
    
    except Exception as e:
        logger.error(f"Error getting order stats: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error getting statistics'
        }, status=500)