from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.info.models import Info

User = get_user_model()


class InfoAdminFilterTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='secret1234', is_staff=True)
        self.owner = User.objects.create_user(username='owner', password='secret1234')
        self.other = User.objects.create_user(username='other', password='secret1234')

        Info.objects.create(name='Alice', age=30, address='A', email='a@example.com', user=self.owner)
        self.other_info = Info.objects.create(
            name='Bob', age=40, address='B', email='b@example.com', user=self.other
        )

    def _count(self, params=None):
        response = self.client.get(reverse('info:info_list'), params or {})
        self.assertEqual(response.status_code, 200)
        return response.context['infos'].paginator.count

    def test_admin_sees_records_of_every_user(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse('info:info_list'))

        self.assertEqual(response.context['infos'].paginator.count, 2)
        self.assertContains(response, 'Alice')
        self.assertContains(response, 'Bob')
        self.assertContains(response, 'All users')

    def test_admin_can_filter_by_owner(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse('info:info_list'), {'user': self.other.pk})

        self.assertEqual(response.context['infos'].paginator.count, 1)
        self.assertContains(response, 'Bob')
        self.assertNotContains(response, 'Alice')

    def test_regular_user_sees_only_own_records_and_filter_is_ignored(self):
        self.client.force_login(self.owner)

        self.assertEqual(self._count(), 1)
        response = self.client.get(reverse('info:info_list'), {'user': self.other.pk})

        self.assertEqual(response.context['infos'].paginator.count, 1)
        self.assertNotContains(response, 'Bob')
        self.assertNotContains(response, 'All users')

    def test_admin_can_open_another_users_record(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse('info:info_get_ajax', args=[self.other_info.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'Bob')

    def test_pagination_preserves_user_filter(self):
        for index in range(11):
            Info.objects.create(
                name=f'Record {index}', age=25, address='C', email='', user=self.other
            )
        self.client.force_login(self.admin)

        response = self.client.get(reverse('info:info_list'), {'user': self.other.pk})

        self.assertEqual(response.context['infos'].paginator.count, 12)
        self.assertEqual(response.context['pagination_query'], f'user={self.other.pk}&')
