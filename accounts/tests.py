from django.test import TestCase
from django.urls import reverse
from .models import Accounts


class RegistrationTests(TestCase):
	def test_signup_creates_account_with_hashed_password(self):
		response = self.client.post(reverse('register'), {
			'first_name': 'Sam',
			'last_name': 'Example',
			'email': 'sam@example.com',
			'phone_number': '1234567890',
			'password': 'simple-password-123',
			'confirm_password': 'simple-password-123',
		})

		self.assertRedirects(response, reverse('home'))
		user = Accounts.objects.get(email='sam@example.com')
		self.assertEqual(user.username, 'sam@example.com')
		self.assertTrue(user.check_password('simple-password-123'))
		self.assertTrue(user.is_active)

	def test_signup_rejects_different_passwords(self):
		response = self.client.post(reverse('register'), {
			'first_name': 'Sam',
			'last_name': 'Example',
			'email': 'sam@example.com',
			'password': 'simple-password-123',
			'confirm_password': 'different-password',
		})

		self.assertEqual(response.status_code, 200)
		self.assertFalse(Accounts.objects.exists())
		self.assertContains(response, 'Passwords do not match.')

	def test_signup_shows_password_error(self):
		response = self.client.post(reverse('register'), {
			'first_name': 'Sam',
			'last_name': 'Example',
			'email': 'sam@example.com',
			'password': '123',
			'confirm_password': '123',
		})

		self.assertEqual(response.status_code, 200)
		self.assertIn('password', response.context['form'].errors)
