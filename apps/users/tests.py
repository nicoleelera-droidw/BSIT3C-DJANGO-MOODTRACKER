from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.access import SUPERUSER_DENIED_MESSAGE

User = get_user_model()


class UserManagementAccessTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='owner', password='secret1234'
        )
        self.staff = User.objects.create_user(
            username='staff', password='secret1234', is_staff=True
        )
        self.regular = User.objects.create_user(
            username='regular', password='secret1234'
        )

    def test_regular_user_is_redirected_with_friendly_message(self):
        self.client.force_login(self.regular)

        response = self.client.get(reverse('users:user_list'), follow=True)

        self.assertRedirects(response, reverse('dashboard'))
        self.assertContains(response, 'Only site administrators can manage user accounts.')

    def test_staff_cannot_manage_users(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse('users:user_list'), follow=True)

        self.assertRedirects(response, reverse('dashboard'))
        self.assertContains(response, 'Only site administrators can manage user accounts.')

    def test_superuser_can_view_users(self):
        self.client.force_login(self.superuser)

        response = self.client.get(reverse('users:user_list'))

        self.assertEqual(response.status_code, 200)

    def test_user_ajax_endpoints_reject_non_superusers(self):
        self.client.force_login(self.staff)

        response = self.client.get(reverse('users:user_list_ajax'))

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], SUPERUSER_DENIED_MESSAGE)
