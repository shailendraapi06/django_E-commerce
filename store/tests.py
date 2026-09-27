from django.test import TestCase
from django.urls import reverse
from category.models import Category
from .models import Product


class HomePageTests(TestCase):
	def test_home_page_shows_product_image_and_name(self):
		category = Category.objects.create(category_name='Clothing', slug='clothing')
		Product.objects.create(
			product_name='Test shirt',
			slug='test-shirt',
			price='20.00',
			images='photos/products/test-shirt.jpg',
			stock=10,
			category=category,
		)

		response = self.client.get(reverse('home'))

		self.assertContains(response, 'Test shirt')
		self.assertContains(response, '/media/photos/products/test-shirt.jpg')
