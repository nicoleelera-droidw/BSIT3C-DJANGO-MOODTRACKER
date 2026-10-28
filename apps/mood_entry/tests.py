from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.message.models import Message
from apps.mood_category.models import MoodCategory
from apps.mood_entry.models import MoodEntry

User = get_user_model()


class MoodEntryCrudTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='secret1234')
        self.other = User.objects.create_user(username='other', password='secret1234')
        self.category = MoodCategory.objects.create(name='Happy')
        self.sad = MoodCategory.objects.create(name='Sad')

    def test_create_redirects_to_detail_and_generates_message(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('mood_entry:mood_entry_create'),
            {'category': self.category.pk, 'rating': '8', 'notes': 'A good day'},
        )

        entry = MoodEntry.objects.get(user=self.user)
        self.assertRedirects(response, reverse('mood_entry:mood_entry_detail', args=[entry.pk]))
        self.assertTrue(Message.objects.filter(mood_entry=entry).exists())
        self.assertContains(self.client.get(reverse('mood_entry:mood_entry_detail', args=[entry.pk])), 'A good day')

    def test_update_regenerates_support_message(self):
        entry = MoodEntry.objects.create(category=self.category, user=self.user)
        Message.objects.create(mood_entry=entry, body='old message')
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('mood_entry:mood_entry_update', args=[entry.pk]),
            {'category': self.sad.pk, 'rating': '3', 'notes': 'Feeling low'},
        )

        entry.refresh_from_db()
        self.assertRedirects(response, reverse('mood_entry:mood_entry_detail', args=[entry.pk]))
        self.assertEqual(entry.category, self.sad)
        self.assertEqual(entry.messages.count(), 1)
        self.assertNotEqual(entry.messages.first().body, 'old message')

    def test_other_user_cannot_view_edit_or_delete(self):
        entry = MoodEntry.objects.create(category=self.category, user=self.user)
        self.client.force_login(self.other)

        self.assertEqual(
            self.client.get(reverse('mood_entry:mood_entry_detail', args=[entry.pk])).status_code, 404
        )
        self.assertEqual(
            self.client.post(
                reverse('mood_entry:mood_entry_update', args=[entry.pk]),
                {'category': self.category.pk, 'rating': ''},
            ).status_code,
            404,
        )
        self.assertEqual(
            self.client.post(reverse('mood_entry:mood_entry_delete', args=[entry.pk])).status_code, 404
        )

    def test_delete_requires_post(self):
        entry = MoodEntry.objects.create(category=self.category, user=self.user)
        self.client.force_login(self.user)

        self.assertEqual(
            self.client.get(reverse('mood_entry:mood_entry_delete', args=[entry.pk])).status_code, 405
        )

        self.client.post(reverse('mood_entry:mood_entry_delete', args=[entry.pk]))

        self.assertFalse(MoodEntry.objects.filter(pk=entry.pk).exists())

    def test_invalid_rating_shows_form_error(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('mood_entry:mood_entry_create'),
            {'category': self.category.pk, 'rating': '99', 'notes': ''},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Rating must be between 1 and 10.')
        self.assertFalse(MoodEntry.objects.filter(user=self.user).exists())

    def test_create_form_prefills_category_from_query_string(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('mood_entry:mood_entry_create'), {'category': self.sad.pk}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form_data']['category'], str(self.sad.pk))


class MoodEntryFilterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='secret1234')
        other = User.objects.create_user(username='other', password='secret1234')
        self.category = MoodCategory.objects.create(name='Happy')
        self.sad = MoodCategory.objects.create(name='Sad')
        self.client.force_login(self.user)

        self.today_entry = MoodEntry.objects.create(
            category=self.category, notes='feel good', user=self.user
        )
        self.old_entry = MoodEntry.objects.create(
            category=self.sad, notes='feel low', user=self.user
        )
        MoodEntry.objects.filter(pk=self.old_entry.pk).update(
            created_at=timezone.now() - timedelta(days=10)
        )
        MoodEntry.objects.create(category=self.category, notes='someone else', user=other)

    def _results(self, params):
        response = self.client.get(reverse('mood_entry:mood_entry_list'), params)
        self.assertEqual(response.status_code, 200)
        return response.context['mood_entries'].paginator.count

    def test_list_only_contains_own_entries(self):
        self.assertEqual(self._results({}), 2)

    def test_filter_by_category(self):
        self.assertEqual(self._results({'category': self.category.pk}), 1)
        self.assertEqual(self._results({'category': self.sad.pk}), 1)

    def test_filter_by_date_range(self):
        today = timezone.localdate()
        self.assertEqual(self._results({'date_from': today.isoformat()}), 1)
        self.assertEqual(
            self._results({'date_to': (today - timedelta(days=5)).isoformat()}), 1
        )

    def test_filter_by_search(self):
        self.assertEqual(self._results({'q': 'feel good'}), 1)

    def test_invalid_filter_values_are_ignored(self):
        self.assertEqual(
            self._results({'category': 'abc', 'date_from': 'not-a-date', 'date_to': '???'}), 2
        )

    def test_pagination_query_preserves_filters(self):
        for _ in range(11):
            MoodEntry.objects.create(category=self.sad, user=self.user)

        response = self.client.get(
            reverse('mood_entry:mood_entry_list'), {'category': self.sad.pk}
        )

        self.assertEqual(response.context['mood_entries'].paginator.count, 12)
        self.assertEqual(response.context['pagination_query'], f'category={self.sad.pk}&')
