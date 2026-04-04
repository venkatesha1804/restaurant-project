# Base_App/views.py - COPY ENTIRE FILE!

from django.db.models import Q, Sum, Count, Min, Max, Avg
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Prefetch
from django.http import JsonResponse
import logging
import razorpay
from django.conf import settings

from Base_App.forms import BookTableForm, FeedbackForm, ContactForm, ItemRatingForm
from Base_App.models import (
    Cart, CartItem, Order, OrderItem, Items, BookTable, AboutUs, Feedback, 
    ItemList, FavoriteItem, SpecialOffer, ItemRating, Wishlist, 
    Coupon, OrderReview, DailySpecial
)

logger = logging.getLogger(__name__)

# ============================================================================
# AUTHENTICATION
# ============================================================================

@require_http_methods(["GET", "POST"])
def LoginView(request):
    if request.user.is_authenticated:
        return redirect('Home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user:
                login(request, user)
                messages.success(request, f'✓ Welcome back!')
                return redirect(request.GET.get('next', 'Home'))
        messages.error(request, '✗ Invalid credentials')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@require_http_methods(["GET", "POST"])
def SignupView(request):
    if request.user.is_authenticated:
        return redirect('Home')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '✓ Account created!')
            return redirect('Home')
    else:
        form = UserCreationForm()
    return render(request, 'login.html', {'form': form, 'is_signup': True})

@require_http_methods(["POST"])
def LogoutView(request):
    logout(request)
    messages.success(request, '✓ Logged out')
    return redirect('Home')

# ============================================================================
# MAIN PAGES
# ============================================================================

def HomeView(request):
    try:
        categories = ItemList.objects.filter(is_active=True).prefetch_related(Prefetch('items', queryset=Items.objects.filter(is_available=True))).order_by('display_order')
        reviews = Feedback.objects.filter(is_approved=True).order_by('-created_at')[:5]
        now = timezone.now()
        special_offers = SpecialOffer.objects.filter(is_active=True, valid_from__lte=now, valid_until__gte=now).order_by('-valid_from')[:2]
        daily_specials = DailySpecial.objects.filter(is_active=True, date=timezone.now().date()).select_related('item')[:6]
        avg_rating = Feedback.objects.filter(is_approved=True).aggregate(avg=Avg('rating'))['avg'] or 0
        return render(request, 'home.html', {'categories': categories, 'reviews': reviews, 'special_offers': special_offers, 'daily_specials': daily_specials, 'avg_rating': round(avg_rating, 1)})
    except Exception as e:
        logger.error(f"Error in HomeView: {str(e)}")
        return render(request, 'home.html')

def AboutView(request):
    try:
        about_data = AboutUs.objects.first()
        return render(request, 'about.html', {'data': about_data})
    except Exception as e:
        logger.error(f"Error in AboutView: {str(e)}")
        return render(request, 'about.html')

def MenuView(request):
    try:
        categories = ItemList.objects.filter(is_active=True).prefetch_related(Prefetch('items', queryset=Items.objects.filter(is_available=True))).order_by('display_order')
        items = Items.objects.filter(is_available=True).select_related('category')
        category_id = request.GET.get('category')
        if category_id:
            try:
                items = items.filter(category_id=int(category_id))
            except (ValueError, TypeError):
                pass
        search_query = request.GET.get('q')
        if search_query:
            items = items.filter(Q(item_name__icontains=search_query) | Q(description__icontains=search_query))
        return render(request, 'menu.html', {'list': categories, 'items': items, 'selected_category': category_id, 'search_query': search_query})
    except Exception as e:
        logger.error(f"Error in MenuView: {str(e)}")
        return render(request, 'menu.html')

# ============================================================================
# BOOKING & FEEDBACK
# ============================================================================

@require_http_methods(["GET", "POST"])
def BookTableView(request):
    if request.method == 'POST':
        form = BookTableForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.status = 'pending'
            booking.save()
            try:
                send_booking_confirmation_email(booking)
            except:
                pass
            messages.success(request, f'✓ Table booked for {booking.total_persons}!')
            return redirect('Book_Table')
    else:
        form = BookTableForm()
    return render(request, 'book_table.html', {'form': form})

def send_booking_confirmation_email(booking):
    try:
        send_mail(f'Booking Confirmation - {booking.name}', f'Your table is booked for {booking.booking_date} at {booking.booking_time}', settings.DEFAULT_FROM_EMAIL, [booking.email], fail_silently=True)
    except Exception as e:
        logger.error(f"Email error: {str(e)}")

@require_http_methods(["GET", "POST"])
def FeedbackView(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST, request.FILES)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.is_approved = False
            feedback.save()
            messages.success(request, '✓ Thank you for your feedback!')
            return redirect('Feedback_Form')
    else:
        form = FeedbackForm()
    approved_feedbacks = Feedback.objects.filter(is_approved=True).order_by('-created_at')[:10]
    return render(request, 'feedback.html', {'form': form, 'feedbacks': approved_feedbacks})

@require_http_methods(["POST"])
def add_to_favorites(request, item_id):
    try:
        user_ip = get_client_ip(request)
        item = Items.objects.get(id=item_id)
        favorite, created = FavoriteItem.objects.get_or_create(user_ip=user_ip, item=item)
        if created:
            return JsonResponse({'success': True, 'message': f'✓ Added!'})
        else:
            favorite.delete()
            return JsonResponse({'success': True, 'message': f'✗ Removed'})
    except Exception as e:
        return JsonResponse({'success': False}, status=500)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

# ============================================================================
# SEARCH & RATINGS
# ============================================================================

@require_http_methods(["GET"])
def search_items(request):
    try:
        items = Items.objects.filter(is_available=True).select_related('category')
        search_query = request.GET.get('q', '').strip()
        if search_query:
            items = items.filter(Q(item_name__icontains=search_query) | Q(description__icontains=search_query) | Q(category__category_name__icontains=search_query))
        category_id = request.GET.get('category')
        if category_id:
            try:
                items = items.filter(category_id=int(category_id))
            except (ValueError, TypeError):
                pass
        return render(request, 'search_results.html', {'items': items, 'search_query': search_query, 'result_count': items.count()})
    except Exception as e:
        logger.error(f"Error in search: {str(e)}")
        return redirect('Menu')

@require_http_methods(["GET"])
def item_detail(request, item_id):
    try:
        item = get_object_or_404(Items, id=item_id, is_available=True)
        ratings = ItemRating.objects.filter(item=item, is_approved=True).order_by('-created_at')
        avg_rating_data = ItemRating.objects.filter(item=item, is_approved=True).aggregate(Avg('rating'))
        average_rating = avg_rating_data['rating__avg'] or 0
        return render(request, 'item_detail.html', {'item': item, 'ratings': ratings, 'average_rating': round(average_rating, 1), 'rating_count': ratings.count()})
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return redirect('Menu')

@require_http_methods(["GET", "POST"])
def rate_item(request, item_id):
    try:
        item = get_object_or_404(Items, id=item_id, is_available=True)
        if request.method == 'POST':
            form = ItemRatingForm(request.POST)
            if form.is_valid():
                rating = form.save(commit=False)
                rating.item = item
                rating.is_approved = False
                rating.save()
                messages.success(request, '✓ Rating submitted!')
                return redirect('item_detail', item_id=item_id)
        else:
            form = ItemRatingForm()
        return render(request, 'rate_item.html', {'item': item, 'form': form})
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return redirect('Menu')

# ============================================================================
# ADMIN
# ============================================================================

@login_required(login_url='login')
def admin_dashboard(request):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, '✗ Access denied')
        return redirect('Home')
    try:
        return render(request, 'admin_dashboard.html', {'total_items': Items.objects.filter(is_available=True).count(), 'pending_bookings': BookTable.objects.filter(status='pending').count()})
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return render(request, 'admin_dashboard.html')

@require_http_methods(["GET", "POST"])
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                send_mail(f'Contact: {form.cleaned_data["subject"]}', form.cleaned_data['message'], settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_FROM_EMAIL], fail_silently=True)
                messages.success(request, '✓ Message sent!')
                return redirect('contact')
            except Exception as e:
                logger.error(f"Error: {str(e)}")
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})

# ============================================================================
# CART
# ============================================================================

def get_or_create_cart(request):
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
    try:
        item = get_object_or_404(Items, id=item_id, is_available=True)
        cart = get_or_create_cart(request)
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
        cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        else:
            cart_item.quantity = quantity
            cart_item.save()
        return JsonResponse({'success': True, 'message': f'✓ Added to cart!', 'cart_count': cart.get_total_quantity(), 'total_price': float(cart.get_total_price())})
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return JsonResponse({'success': False}, status=500)

@require_http_methods(["GET"])
def view_cart(request):
    try:
        cart = get_or_create_cart(request)
        cart_items = CartItem.objects.filter(cart=cart)
        return render(request, 'cart.html', {'cart': cart, 'cart_items': cart_items, 'total_price': cart.get_total_price(), 'total_items': cart.get_total_items()})
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return redirect('Menu')

@require_http_methods(["POST"])
def update_cart_item(request, item_id):
    try:
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, cart=cart, item_id=item_id)
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            cart_item.delete()
            message = '✓ Removed'
        else:
            cart_item.quantity = quantity
            cart_item.save()
            message = '✓ Updated'
        return JsonResponse({'success': True, 'message': message, 'cart_count': cart.get_total_quantity(), 'total_price': float(cart.get_total_price())})
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return JsonResponse({'success': False}, status=500)

@require_http_methods(["POST"])
def remove_from_cart(request, item_id):
    try:
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, cart=cart, item_id=item_id)
        item_name = cart_item.item.item_name
        cart_item.delete()
        return JsonResponse({'success': True, 'message': f'✓ {item_name} removed', 'cart_count': cart.get_total_quantity(), 'total_price': float(cart.get_total_price())})
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return JsonResponse({'success': False}, status=500)

@require_http_methods(["POST"])
def clear_cart(request):
    try:
        cart = get_or_create_cart(request)
        cart.clear_cart()
        return JsonResponse({'success': True, 'message': '✓ Cleared'})
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return JsonResponse({'success': False}, status=500)

@require_http_methods(["GET"])
def get_cart_count(request):
    try:
        cart = get_or_create_cart(request)
        return JsonResponse({'cart_count': cart.get_total_quantity(), 'total_price': float(cart.get_total_price())})
    except Exception as e:
        return JsonResponse({'cart_count': 0, 'total_price': 0})

# ============================================================================
# CHECKOUT & ORDERS
# ============================================================================

@require_http_methods(["GET", "POST"])
def checkout(request):
    try:
        cart = get_or_create_cart(request)
        cart_items = CartItem.objects.filter(cart=cart)
        if not cart_items.exists():
            messages.error(request, '❌ Cart is empty')
            return redirect('view_cart')
        if request.method == 'POST':
            customer_name = request.POST.get('customer_name', '').strip()
            customer_email = request.POST.get('customer_email', '').strip()
            customer_phone = request.POST.get('customer_phone', '').strip()
            delivery_address = request.POST.get('delivery_address', '').strip()
            delivery_pincode = request.POST.get('delivery_pincode', '').strip()
            coupon_code = request.POST.get('coupon_code', '').strip()
            if not all([customer_name, customer_email, customer_phone, delivery_address, delivery_pincode]):
                messages.error(request, '❌ Please fill all required fields')
                return render(request, 'checkout.html', {'cart': cart, 'cart_items': cart_items, 'total_price': cart.get_total_price()})
            total_amount = cart.get_total_price()
            if coupon_code:
                try:
                    coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                    if coupon.is_valid() and total_amount >= coupon.min_order_amount:
                        discount = (total_amount * coupon.discount_percent) / 100
                        total_amount -= discount
                        coupon.times_used += 1
                        coupon.save()
                except Coupon.DoesNotExist:
                    pass
            order = Order.objects.create(customer_name=customer_name, customer_email=customer_email, customer_phone=customer_phone, delivery_address=delivery_address, delivery_pincode=delivery_pincode, total_amount=total_amount, status='pending', payment_status='pending')
            for cart_item in cart_items:
                OrderItem.objects.create(order=order, item=cart_item.item, quantity=cart_item.quantity, price_at_purchase=cart_item.item.price, subtotal=cart_item.get_subtotal())
            cart.clear_cart()
            messages.success(request, '✅ Order created! Proceeding to payment...')
            return redirect('create_payment', order_id=order.id)
        return render(request, 'checkout.html', {'cart': cart, 'cart_items': cart_items, 'total_price': cart.get_total_price()})
    except Exception as e:
        logger.error(f"Checkout error: {str(e)}")
        messages.error(request, f'❌ Error: {str(e)}')
        return redirect('view_cart')

@require_http_methods(["GET"])
def order_confirmation(request, order_id):
    try:
        order = get_object_or_404(Order, id=order_id)
        return render(request, 'order_confirmation.html', {'order': order, 'order_items': order.items.all()})
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return redirect('Home')

@require_http_methods(["GET"])
def order_history(request):
    if not request.user.is_authenticated:
        messages.error(request, '✗ Please login')
        return redirect('login')
    orders = Order.objects.filter(customer_email=request.user.email).order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})

@require_http_methods(["GET"])
def order_detail(request, order_id):
    try:
        order = get_object_or_404(Order, id=order_id)
        if request.user.is_authenticated and order.customer_email != request.user.email:
            if not request.user.is_staff:
                messages.error(request, '✗ Access denied')
                return redirect('Home')
        return render(request, 'order_detail.html', {'order': order, 'order_items': order.items.all()})
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return redirect('Home')

@require_http_methods(["POST"])
def update_order_status(request, order_id):
    try:
        if not request.user.is_staff:
            return JsonResponse({'success': False}, status=403)
        order = get_object_or_404(Order, id=order_id)
        order.status = request.POST.get('status')
        order.save()
        return JsonResponse({'success': True, 'message': '✓ Updated'})
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return JsonResponse({'success': False}, status=500)

# ============================================================================
# ADMIN ORDERS
# ============================================================================

def admin_required(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(admin_required)
def admin_orders(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'admin_orders.html', {'orders': orders, 'total_orders': Order.objects.count()})

@login_required
@user_passes_test(admin_required)
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin_order_detail.html', {'order': order, 'order_items': order.items.all()})

@login_required
@user_passes_test(admin_required)
@require_http_methods(["POST"])
def admin_update_order_status(request, order_id):
    try:
        order = get_object_or_404(Order, id=order_id)
        order.status = request.POST.get('status')
        order.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False}, status=500)

@login_required
@user_passes_test(admin_required)
def admin_order_stats(request):
    today = timezone.now().date()
    return JsonResponse({'success': True, 'today_count': Order.objects.filter(created_at__date=today).count()})

# ============================================================================
# 🔴 RAZORPAY PAYMENT - CRITICAL FIX ✅
# ============================================================================

@require_http_methods(["GET"])
def create_payment(request, order_id):
    """Show payment.html with Razorpay button"""
    try:
        order = get_object_or_404(Order, id=order_id)
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({'amount': int(order.total_amount * 100), 'currency': 'INR', 'receipt': f'order_{order.id}', 'payment_capture': 1})
        logger.info(f"Payment page for Order #{order.id}")
        
        # 🔴 CRITICAL: Return payment.html
        return render(request, 'payment.html', {
            'order': order,
            'razorpay_order': razorpay_order,
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        })
    except Exception as e:
        logger.error(f"Payment error: {str(e)}")
        messages.error(request, f'❌ Error: {str(e)}')
        return redirect('order_detail', order_id=order_id)

@require_http_methods(["POST"])
def payment_success(request):
    """Verify and process payment"""
    try:
        order_id = request.POST.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature({'razorpay_order_id': request.POST.get('razorpay_order_id'), 'razorpay_payment_id': request.POST.get('razorpay_payment_id'), 'razorpay_signature': request.POST.get('razorpay_signature')})
            order.payment_status = 'completed'
            order.status = 'confirmed'
            order.save()
            logger.info(f"Payment success for Order #{order.id}")
            messages.success(request, '✅ Payment successful!')
            return redirect('order_confirmation', order_id=order.id)
        except Exception as e:
            order.payment_status = 'failed'
            order.save()
            logger.error(f"Payment failed: {str(e)}")
            messages.error(request, '❌ Payment verification failed')
            return redirect('order_detail', order_id=order.id)
    except Exception as e:
        logger.error(f"Payment error: {str(e)}")
        return redirect('Home')

# ============================================================================
# FEATURES
# ============================================================================

@require_http_methods(["POST"])
def add_to_wishlist(request, item_id):
    try:
        item = get_object_or_404(Items, id=item_id)
        if request.user.is_authenticated:
            wishlist, created = Wishlist.objects.get_or_create(user=request.user, item=item)
            if created:
                return JsonResponse({'success': True, 'message': '✓ Added to wishlist!'})
            else:
                wishlist.delete()
                return JsonResponse({'success': True, 'message': '✗ Removed'})
        else:
            return JsonResponse({'success': False, 'message': '✗ Login required'}, status=401)
    except Exception as e:
        return JsonResponse({'success': False}, status=500)

@login_required
def my_wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('item')
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})

@require_http_methods(["POST"])
def apply_coupon(request):
    try:
        code = request.POST.get('coupon_code', '').upper()
        coupon = Coupon.objects.get(code=code, is_active=True)
        if timezone.now() > coupon.expiry_date:
            return JsonResponse({'success': False, 'message': '✗ Expired'})
        return JsonResponse({'success': True, 'discount_percent': coupon.discount_percent, 'message': f'✓ {coupon.discount_percent}% discount!'})
    except Coupon.DoesNotExist:
        return JsonResponse({'success': False, 'message': '✗ Invalid code'})
    except Exception as e:
        return JsonResponse({'success': False}, status=500)

@require_http_methods(["POST"])
def submit_order_review(request, order_id):
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': '✗ Login required'}, status=401)
        order = get_object_or_404(Order, id=order_id)
        if order.customer_email != request.user.email and not request.user.is_staff:
            return JsonResponse({'success': False}, status=403)
        OrderReview.objects.create(order=order, user=request.user, rating=request.POST.get('rating'), review=request.POST.get('review'), is_approved=False)
        return JsonResponse({'success': True, 'message': '✓ Review submitted'})
    except Exception as e:
        return JsonResponse({'success': False}, status=500)

def get_recommendations(request):
    try:
        category_id = request.GET.get('category_id')
        if not category_id:
            items = Items.objects.filter(is_available=True).order_by('?')[:6]
        else:
            items = Items.objects.filter(category_id=category_id, is_available=True).order_by('?')[:6]
        recommendations = []
        for item in items:
            avg_rating = ItemRating.objects.filter(item=item, is_approved=True).aggregate(Avg('rating'))['rating__avg'] or 0
            recommendations.append({'id': item.id, 'name': item.item_name, 'price': float(item.price), 'rating': round(avg_rating, 1), 'image': item.image.url})
        return JsonResponse({'success': True, 'recommendations': recommendations})
    except Exception as e:
        return JsonResponse({'success': False}, status=500)

@login_required(login_url='login')
def approve_feedback(request, feedback_id):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, '✗ Access denied')
        return redirect('Home')
    feedback = get_object_or_404(Feedback, id=feedback_id)
    feedback.is_approved = True
    feedback.save()
    messages.success(request, f'✓ Feedback approved')
    return redirect('admin_dashboard')

@login_required(login_url='login')
def reject_feedback(request, feedback_id):
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, '✗ Access denied')
        return redirect('Home')
    feedback = get_object_or_404(Feedback, id=feedback_id)
    feedback.delete()
    messages.success(request, f'✓ Feedback rejected')
    return redirect('admin_dashboard')
# ============================================================================
# COPY THIS FUNCTION INTO Base_App/views.py
# REPLACE the send_booking_confirmation_email function with this!
# ============================================================================

def send_booking_confirmation_email(booking):
    """Send table booking confirmation email - FIXED"""
    try:
        subject = f"🎉 Table Booking Confirmed #{booking.id} - Feane Restaurant"
        
        message = f"""
Hi {booking.name},

Thank you for booking a table at Feane Restaurant! We're excited to have you.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 YOUR BOOKING DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Booking ID:          #{booking.id}
Name:                {booking.name}
Phone:               {booking.phone_number}
Email:               {booking.email}
Date:                {booking.booking_date.strftime('%A, %B %d, %Y')}
Time:                {booking.booking_time.strftime('%I:%M %p')}
Number of Persons:   {booking.total_persons}
Status:              ✓ Confirmed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 RESTAURANT LOCATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Koramangala, Bangalore, Karnataka
📞 Phone: +91 9876543210
🌐 Website: feanerestaurant.com

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏰ IMPORTANT INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Please arrive 10 minutes before your reservation
✓ Reservations are held for 15 minutes after booking time
✓ We accept cash and card payments
✓ Special requests can be accommodated upon request

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❓ NEED TO CANCEL OR MODIFY?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please contact us as soon as possible:
📞 Call: +91 9876543210
📧 Email: support@feanefoods.com

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

We're looking forward to serving you delicious food and excellent service!

Best regards,
Feane Restaurant Team 🍽️

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
© 2026 Feane Restaurant. All rights reserved.
This is an automated email. Please do not reply to this message.
"""
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.email],
            fail_silently=False,  # This will show errors
        )
        
        logger.info(f"✅ Booking confirmation email SENT to {booking.email}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error sending email: {str(e)}")
        print(f"EMAIL ERROR: {str(e)}")  # Also print to console
        return False