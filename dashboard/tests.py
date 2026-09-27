from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse


class AuthorizationTests(TestCase):
	def setUp(self):
		self.user_model = get_user_model()
		self.customer = self.user_model.objects.create_user(
			email='customer@example.com',
			username='customer',
			password='strong-password-123',
		)
		self.staff = self.user_model.objects.create_user(
			email='staff@example.com',
			username='staff',
			password='strong-password-123',
			is_staff=True,
		)

	def test_customer_cannot_access_dashboard(self):
		self.client.force_login(self.customer)

		response = self.client.get(reverse('dashboard:home'))

		self.assertEqual(response.status_code, 302)

	def test_customer_cannot_access_django_admin(self):
		self.client.force_login(self.customer)

		response = self.client.get('/admin/')

		self.assertEqual(response.status_code, 302)
		self.assertIn('/admin/login/', response.url)

	def test_staff_can_access_dashboard(self):
		self.client.force_login(self.staff)

		response = self.client.get(reverse('dashboard:home'))

		self.assertEqual(response.status_code, 200)

	def test_setup_command_creates_expected_groups_and_permissions(self):
		call_command('setup_authorization')

		self.assertEqual(Group.objects.count(), 4)
		product_manager = Group.objects.get(name='Product Manager')
		self.assertTrue(
			product_manager.permissions.filter(
				codename='change_product',
			).exists()
		)
