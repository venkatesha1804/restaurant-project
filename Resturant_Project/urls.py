from django.contrib import admin
from django.urls import path
from Base_App.views import health_check
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
    download_invoice,
    update_order_status,
    admin_orders,
    admin_order_detail,
    admin_update_order_status,
    admin_order_stats,
    search_items,
    item_detail,
    rate_item,
    create_payment,
    payment_success,
    add_to_wishlist,
    cancel_order,

    my_wishlist,
    apply_coupon,
    submit_order_review,
    get_recommendations,
)

urlpatterns = [
    # your existing paths...

    path('health/', health_check, name='health_check'),

    path('admin/', admin.site.urls),
    
    path('', HomeView, name="Home"),
    path('menu/', MenuView, name='Menu'),
    path('about/', AboutView, name='About'),
    
    path('book-table/', BookTableView, name='Book_Table'),
    path('feedback/', FeedbackView, name='Feedback_Form'),
    path('contact/', contact_view, name='contact'),
    
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    
    path('login/', LoginView, name='login'),
    path('signup/', SignupView, name='signup'),
    path('logout/', LogoutView, name='logout'),
    
    path('cart/', view_cart, name='view_cart'),
    path('add-to-cart/<int:item_id>/', add_to_cart, name='add_to_cart'),
    path('update-cart/<int:item_id>/', update_cart_item, name='update_cart'),
    path('remove-from-cart/<int:item_id>/', remove_from_cart, name='remove_from_cart'),
    path('clear-cart/', clear_cart, name='clear_cart'),
    path('get-cart-count/', get_cart_count, name='get_cart_count'),
    
    path('checkout/', checkout, name='checkout'),
    path('order/confirmation/<int:order_id>/', order_confirmation, name='order_confirmation'),
    path('order/history/', order_history, name='order_history'),
    path('order/<int:order_id>/', order_detail, name='order_detail'),
    path('order/<int:order_id>/invoice/',
    download_invoice,
    name='download_invoice'),
    path(
    'order/<int:order_id>/cancel/',
    cancel_order,
    name='cancel_order'
),

    path('order/<int:order_id>/update-status/', update_order_status, name='update_order_status'),
    
    path('payment/<int:order_id>/', create_payment, name='create_payment'),
    path('payment/success/', payment_success, name='payment_success'),
    
    path('admin/orders/', admin_orders, name='admin_orders'),
    path('admin/order/<int:order_id>/', admin_order_detail, name='admin_order_detail'),
    path('admin/order/<int:order_id>/status/', admin_update_order_status, name='admin_update_order_status'),
    path('admin/order/stats/', admin_order_stats, name='admin_order_stats'),
    
    path('search/', search_items, name='search'),
    path('item/<int:item_id>/', item_detail, name='item_detail'),
    path('item/<int:item_id>/rate/', rate_item, name='rate_item'),
    
    path('add-to-favorites/<int:item_id>/', add_to_favorites, name='add_to_favorites'),
    
    # New Features
    path('wishlist/add/<int:item_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/my-wishlist/', my_wishlist, name='my_wishlist'),
    path('coupon/apply/', apply_coupon, name='apply_coupon'),
    path('order/<int:order_id>/review/', submit_order_review, name='submit_order_review'),
    path('api/recommendations/', get_recommendations, name='get_recommendations'),
    
    # Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)