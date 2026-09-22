from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from Base_App.models import (
    ItemList, Items, Cart, CartItem, Order, OrderItem, Coupon, BookTable
)


class CartModelTests(TestCase):
    def setUp(self):
        self.category = ItemList.objects.create(category_name='Pizza')
        self.item = Items.objects.create(item_name='Margherita', price=Decimal('199.00'), category=self.category)
        self.cart = Cart.objects.create(session_key='test-session')

    def test_cart_total_price_single_item(self):
        CartItem.objects.create(cart=self.cart, item=self.item, quantity=2)
        self.assertEqual(self.cart.get_total_price(), Decimal('398.00'))

    def test_cart_total_price_multiple_items(self):
        item2 = Items.objects.create(item_name='Pepperoni', price=Decimal('249.00'), category=self.category)
        CartItem.objects.create(cart=self.cart, item=self.item, quantity=1)
        CartItem.objects.create(cart=self.cart, item=item2, quantity=1)
        self.assertEqual(self.cart.get_total_price(), Decimal('448.00'))

    def test_clear_cart_removes_all_items(self):
        CartItem.objects.create(cart=self.cart, item=self.item, quantity=3)
        self.cart.clear_cart()
        self.assertEqual(self.cart.items.count(), 0)

    def test_empty_cart_total_is_zero(self):
        self.assertEqual(self.cart.get_total_price(), 0)


class CouponModelTests(TestCase):
    def setUp(self):
        self.coupon = Coupon.objects.create(
            code='SAVE20', description='20% off', discount_percent=20,
            max_uses=5, expiry_date=timezone.now() + timedelta(days=7)
        )

    def test_valid_coupon_within_limits(self):
        self.assertTrue(self.coupon.is_valid())

    def test_expired_coupon_is_invalid(self):
        self.coupon.expiry_date = timezone.now() - timedelta(days=1)
        self.coupon.save()
        self.assertFalse(self.coupon.is_valid())

    def test_coupon_at_max_uses_is_invalid(self):
        self.coupon.times_used = 5
        self.coupon.save()
        self.assertFalse(self.coupon.is_valid())

    def test_inactive_coupon_is_invalid(self):
        self.coupon.is_active = False
        self.coupon.save()
        self.assertFalse(self.coupon.is_valid())


class OrderTests(TestCase):
    def setUp(self):
        self.category = ItemList.objects.create(category_name='Burger')
        self.item = Items.objects.create(item_name='Cheeseburger', price=Decimal('150.00'), category=self.category)
        self.order = Order.objects.create(
            customer_name='Test User', customer_email='test@example.com',
            customer_phone='9999999999', delivery_address='123 Test St',
            delivery_pincode='560001', total_amount=Decimal('150.00'),
        )

    def test_order_item_subtotal_calculated_on_save(self):
        oi = OrderItem.objects.create(order=self.order, item=self.item, quantity=3, price_at_purchase=Decimal('150.00'))
        self.assertEqual(oi.subtotal, Decimal('450.00'))

    def test_pending_order_can_be_cancelled(self):
        self.assertTrue(self.order.can_be_cancelled())

    def test_delivered_order_cannot_be_cancelled(self):
        self.order.status = 'delivered'
        self.order.save()
        self.assertFalse(self.order.can_be_cancelled())

    def test_get_total_items_sums_quantities(self):
        OrderItem.objects.create(order=self.order, item=self.item, quantity=2, price_at_purchase=Decimal('150.00'))
        item2 = Items.objects.create(item_name='Fries', price=Decimal('80.00'), category=self.category)
        OrderItem.objects.create(order=self.order, item=item2, quantity=3, price_at_purchase=Decimal('80.00'))
        self.assertEqual(self.order.get_total_items(), 5)


class InventoryTests(TestCase):
    def setUp(self):
        self.category = ItemList.objects.create(category_name='Drinks')
        self.item = Items.objects.create(
            item_name='Cola', price=Decimal('50.00'), category=self.category,
            track_inventory=True, stock_quantity=5
        )

    def test_item_in_stock_when_quantity_available(self):
        self.assertTrue(self.item.is_in_stock(3))

    def test_item_out_of_stock_when_quantity_exceeds(self):
        self.assertFalse(self.item.is_in_stock(10))

    def test_untracked_item_always_in_stock(self):
        untracked = Items.objects.create(item_name='Water', price=Decimal('20.00'), category=self.category, track_inventory=False)
        self.assertTrue(untracked.is_in_stock(1000))

    def test_reduce_stock_decreases_quantity(self):
        self.item.reduce_stock(2)
        self.item.refresh_from_db()
        self.assertEqual(self.item.stock_quantity, 3)

    def test_reduce_stock_never_goes_negative(self):
        self.item.reduce_stock(100)
        self.item.refresh_from_db()
        self.assertEqual(self.item.stock_quantity, 0)


class AuthViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_signup_creates_user(self):
        response = self.client.post('/signup/', {
            'username': 'newuser', 'password1': 'ComplexPass123!', 'password2': 'ComplexPass123!'
        })
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_with_valid_credentials(self):
        User.objects.create_user(username='testlogin', password='TestPass123!')
        response = self.client.post('/login/', {'username': 'testlogin', 'password': 'TestPass123!'})
        self.assertEqual(response.status_code, 302)

    def test_login_with_invalid_credentials_shows_error(self):
        response = self.client.post('/login/', {'username': 'ghost', 'password': 'wrong'}, follow=True)
        self.assertContains(response, 'Invalid credentials')


class BookingTests(TestCase):
    def test_pending_booking_can_be_cancelled(self):
        booking = BookTable.objects.create(
            name='Test', email='test@x.com', phone_number='9999999999',
            total_persons=4, booking_date=timezone.now().date() + timedelta(days=1),
        )
        self.assertTrue(booking.can_be_cancelled())

    def test_completed_booking_cannot_be_cancelled(self):
        booking = BookTable.objects.create(
            name='Test', email='test@x.com', phone_number='9999999999',
            total_persons=4, booking_date=timezone.now().date() + timedelta(days=1),
            status='completed'
        )
        self.assertFalse(booking.can_be_cancelled())