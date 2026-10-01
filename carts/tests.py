from django.test import TestCase
from django.urls import reverse
from accounts.models import Accounts
from category.models import Category
from store.models import Product, Variation
from .models import Cart, CartItem


class ProductVariationCartTests(TestCase):
	def setUp(self):
		category = Category.objects.create(category_name='Clothing', slug='clothing')
		self.product = Product.objects.create(
			product_name='Test shirt',
			slug='test-shirt',
			description='A test product',
			price='20.00',
			stock=10,
			category=category,
		)
		self.black = Variation.objects.create(
			product=self.product,
			variation_category=Variation.COLOR,
			variation_value='Black',
		)
		self.blue = Variation.objects.create(
			product=self.product,
			variation_category=Variation.COLOR,
			variation_value='Blue',
		)
		self.medium = Variation.objects.create(
			product=self.product,
			variation_category=Variation.SIZE,
			variation_value='Medium',
		)

	def test_product_page_shows_configured_variations(self):
		response = self.client.get(self.product.get_absolute_url())

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Black')
		self.assertContains(response, 'Medium')
		self.assertNotContains(response, 'Silver')

	def test_selected_variations_are_saved_and_grouped_into_cart_lines(self):
		add_url = reverse('add_cart', args=[self.product.id])
		self.client.post(add_url, {'variation_ids': [self.black.id, self.medium.id]})
		self.client.post(add_url, {'variation_ids': [self.black.id, self.medium.id]})
		self.client.post(add_url, {'variation_ids': [self.blue.id, self.medium.id]})

		cart = Cart.objects.get(cart_id=self.client.session.session_key)
		cart_items = CartItem.objects.filter(cart=cart).order_by('id')
		self.assertEqual(cart_items.count(), 2)

		black_item = cart_items.get(variations=self.black)
		blue_item = cart_items.get(variations=self.blue)
		self.assertEqual(black_item.quantity, 2)
		self.assertEqual(blue_item.quantity, 1)
		self.assertTrue(black_item.variations.filter(id=self.medium.id).exists())

		response = self.client.get(reverse('cart'))
		self.assertContains(response, 'Color: Black')
		self.assertContains(response, 'Size: Medium')
		self.assertContains(response, 'Color: Blue')

		self.client.get(reverse('decrement_cart', args=[black_item.id]))
		black_item.refresh_from_db()
		blue_item.refresh_from_db()
		self.assertEqual(black_item.quantity, 1)
		self.assertEqual(blue_item.quantity, 1)

	def test_add_requires_one_option_for_each_variation_category(self):
		response = self.client.post(
			reverse('add_cart', args=[self.product.id]),
			{'variation_ids': [self.black.id]},
		)

		self.assertEqual(response.status_code, 302)
		self.assertFalse(Cart.objects.exists())
		self.assertFalse(CartItem.objects.exists())

	def test_logged_in_cart_groups_variations_and_updates_counter(self):
		user = Accounts.objects.create_user(
			first_name='Sam',
			last_name='Example',
			username='sam@example.com',
			email='sam@example.com',
			password='simple-password-123',
		)
		user.is_active = True
		user.save()
		self.client.force_login(user)
		add_url = reverse('add_cart', args=[self.product.id])
		self.client.post(add_url, {'variation_ids': [self.black.id, self.medium.id]})
		self.client.post(add_url, {'variation_ids': [self.black.id, self.medium.id]})
		self.client.post(add_url, {'variation_ids': [self.blue.id, self.medium.id]})

		user_items = CartItem.objects.filter(user=user).order_by('id')
		self.assertEqual(user_items.count(), 2)
		self.assertEqual(user_items.get(variations=self.black).quantity, 2)
		self.assertEqual(user_items.get(variations=self.blue).quantity, 1)

		response = self.client.get(reverse('cart'))
		self.assertEqual(response.context['quantity'], 3)
		self.assertEqual(response.context['cart_count'], 3)
		self.assertContains(response, 'Color: Black')
		self.assertContains(response, 'Size: Medium')
		self.assertContains(response, 'Color: Blue')

	def test_logged_in_user_cannot_see_or_change_another_users_cart(self):
		owner = Accounts.objects.create_user(
			first_name='Owner',
			last_name='Example',
			username='owner@example.com',
			email='owner@example.com',
			password='simple-password-123',
		)
		other_user = Accounts.objects.create_user(
			first_name='Other',
			last_name='Example',
			username='other@example.com',
			email='other@example.com',
			password='simple-password-123',
		)
		owner.is_active = True
		owner.save()
		other_user.is_active = True
		other_user.save()
		cart, _ = Cart.objects.get_or_create(cart_id='owner-cart')
		item = CartItem.objects.create(
			product=self.product,
			cart=cart,
			user=owner,
			quantity=1,
		)
		self.client.force_login(other_user)

		response = self.client.get(reverse('cart'))
		self.assertEqual(response.context['quantity'], 0)
		self.assertEqual(response.context['cart_count'], 0)

		self.client.get(reverse('increment_cart', args=[item.id]))
		item.refresh_from_db()
		self.assertEqual(item.quantity, 1)
