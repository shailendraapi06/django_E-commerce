import re

from django.core import mail
from django.test import TestCase, override_settings
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
		self.assertIn('_auth_user_id', self.client.session)

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


class AuthenticationTests(TestCase):
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

	def test_login_accepts_email_and_password(self):
		response = self.client.post(reverse('login'), {
			'username': 'sam@example.com',
			'password': 'simple-password-123',
		})

		self.assertRedirects(response, reverse('home'))
		self.assertIn('_auth_user_id', self.client.session)

	def test_logout_clears_the_session(self):
		self.client.force_login(self.user)

		response = self.client.post(reverse('logout'))

		self.assertRedirects(response, reverse('home'))
		self.assertNotIn('_auth_user_id', self.client.session)

	@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
	def test_password_reset_email_and_new_password(self):
		response = self.client.post(reverse('password_reset'), {
			'email': self.user.email,
		})

		self.assertRedirects(response, reverse('password_reset_done'))
		self.assertEqual(len(mail.outbox), 1)
		self.assertEqual(mail.outbox[0].to, [self.user.email])

		reset_path = re.search(
			r'http://testserver(/accounts/reset/\S+/\S+/)',
			mail.outbox[0].body,
		).group(1)
		response = self.client.get(reset_path)
		self.assertEqual(response.status_code, 302)

		confirm_path = response['Location']
		response = self.client.post(confirm_path, {
			'new_password1': 'new-simple-password-456',
			'new_password2': 'new-simple-password-456',
		})

		self.assertRedirects(response, reverse('password_reset_complete'))
		self.user.refresh_from_db()
		self.assertTrue(self.user.check_password('new-simple-password-456'))
