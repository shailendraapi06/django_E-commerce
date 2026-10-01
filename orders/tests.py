import re
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import Accounts
from carts.models import Cart, CartItem
from category.models import Category
from store.models import Product, Variation
from .models import Order, OrderProduct, Payment


class OrderFlowTests(TestCase):
    def setUp(self):
        self.user = Accounts.objects.create_user(
            first_name='Sam',
            last_name='Example',
            username='sam@example.com',
            email='sam@example.com',
            password='simple-password-123',
        )
        self.user.is_active = True
        self.user.save()
        category = Category.objects.create(category_name='Clothing', slug='clothing')
        self.product = Product.objects.create(
            product_name='Test shirt',
            slug='test-shirt',
            price='20.00',
            stock=10,
            category=category,
        )
        self.color = Variation.objects.create(
            product=self.product,
            variation_category=Variation.COLOR,
            variation_value='Black',
        )
        self.cart, _ = Cart.objects.get_or_create(cart_id='order-test-cart')
        self.cart_item = CartItem.objects.create(
            product=self.product,
            cart=self.cart,
            user=self.user,
            quantity=2,
        )
        self.cart_item.variations.add(self.color)
        self.client.force_login(self.user)
        self.order_data = {
            'first_name': 'Sam',
            'last_name': 'Example',
            'email': 'sam@example.com',
            'phone': '1234567890',
            'address': '1 Main Street',
            'city': 'London',
            'state': 'London',
            'country': 'United Kingdom',
            'postal_code': 'SW1A 1AA',
            'order_note': '',
        }

    def test_checkout_redirects_guest_back_to_checkout_after_login(self):
        self.client.logout()

        response = self.client.get(reverse('checkout'))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('checkout')}",
        )

    def test_place_order_saves_payment_order_items_and_clears_cart(self):
        response = self.client.post(reverse('place_order'), self.order_data)

        order = Order.objects.get(user=self.user)
        payment = Payment.objects.get(user=self.user)
        order_item = OrderProduct.objects.get(order=order)

        self.assertRedirects(response, reverse('order_complete', args=[order.order_number]))
        self.assertRegex(order.order_number, re.compile(r'^\d{8}[A-F0-9]{8}$'))
        self.assertTrue(order.is_ordered)
        self.assertEqual(order.order_total, Decimal('40.00'))
        self.assertEqual(order.tax, Decimal('0.80'))
        self.assertEqual(order.grand_total, Decimal('40.80'))
        self.assertEqual(payment.payment_method, Payment.CASH_ON_DELIVERY)
        self.assertEqual(payment.amount_paid, order.grand_total)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.product_price, Decimal('20.00'))
        self.assertTrue(order_item.variations.filter(id=self.color.id).exists())
        self.assertFalse(CartItem.objects.filter(user=self.user).exists())
        self.assertEqual(self.client.get(response.url).status_code, 200)

    def test_invalid_checkout_does_not_create_order_or_clear_cart(self):
        response = self.client.post(reverse('place_order'), {'email': 'not-an-email'})

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Order.objects.exists())
        self.assertFalse(Payment.objects.exists())
        self.assertTrue(CartItem.objects.filter(id=self.cart_item.id).exists())

    def test_order_confirmation_is_only_visible_to_its_owner(self):
        response = self.client.post(reverse('place_order'), self.order_data)
        order = Order.objects.get(user=self.user)
        other_user = Accounts.objects.create_user(
            first_name='Other',
            last_name='Example',
            username='other@example.com',
            email='other@example.com',
            password='simple-password-123',
        )
        other_user.is_active = True
        other_user.save()
        self.client.force_login(other_user)

        response = self.client.get(reverse('order_complete', args=[order.order_number]))

        self.assertEqual(response.status_code, 404)