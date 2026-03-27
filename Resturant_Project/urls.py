from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from Base_App.views import (
    HomeView, 
    BookTableView, 
    MenuView, 
    AboutView, 
    FeedbackView, 
    SignupView,
    LoginView,
    LogoutView,
    admin_dashboard,
    contact_view,
    add_to_favorites,
    view_cart,
    add_to_cart,
    update_cart_item,
    remove_from_cart,
    clear_cart,
    get_cart_count,
    checkout,
    order_confirmation,
    order_history,
    order_detail,
    update_order_status,
    admin_orders,
    admin_order_detail,
    admin_update_order_status,
    admin_order_stats,
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Home & Main Pages
    path('', HomeView, name="Home"),
    path('menu/', MenuView, name='Menu'),
    path('about/', AboutView, name='About'),
    
    # Booking & Feedback
    path('book-table/', BookTableView, name='Book_Table'),
    path('feedback/', FeedbackView, name='Feedback_Form'),
    path('contact/', contact_view, name='contact'),
    
    # Admin Dashboard
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    
    # Authentication
    path('login/', LoginView, name='login'),
    path('signup/', SignupView, name='signup'),
    path('logout/', LogoutView, name='logout'),
    
    # AJAX Endpoints
    path('add-to-favorites/<int:item_id>/', add_to_favorites, name='add_to_favorites'),
    
    # Shopping Cart URLs
    path('cart/', view_cart, name='view_cart'),
    path('add-to-cart/<int:item_id>/', add_to_cart, name='add_to_cart'),
    path('update-cart/<int:item_id>/', update_cart_item, name='update_cart'),
    path('remove-from-cart/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('clear-cart/', clear_cart, name='clear_cart'),
    path('get-cart-count/', get_cart_count, name='get_cart_count'),
    
    # Checkout & Orders
    path('checkout/', checkout, name='checkout'),
    path('order/confirmation/<int:order_id>/', order_confirmation, name='order_confirmation'),
    path('order/history/', order_history, name='order_history'),
    path('order/<int:order_id>/', order_detail, name='order_detail'),
    path('admin/order/<int:order_id>/update-status/', update_order_status, name='update_order_status'),
    
    # Admin Order Management
    path('admin/orders/', admin_orders, name='admin_orders'),
    path('admin/order/<int:order_id>/', admin_order_detail, name='admin_order_detail'),
    path('admin/order/<int:order_id>/update-status/', admin_update_order_status, name='admin_update_order_status'),
    path('admin/order/stats/', admin_order_stats, name='admin_order_stats'),
]

# Media files handling
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)