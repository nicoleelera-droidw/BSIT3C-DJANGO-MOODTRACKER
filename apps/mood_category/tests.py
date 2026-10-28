from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.mood_entry.models import MoodEntry

from .models import MoodCategory

User = get_user_model()


class MoodCategoryCrudTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username='staff', password='secret1234', is_staff=True)
        self.regular = User.objects.create_user(username='regular', password='secret1234')
        self.category = MoodCategory.objects.create(name='Happy')

    def test_non_staff_cannot_access_category_pages(self):
        self.client.force_login(self.regular)

        response = self.client.get(
            reverse('mood_category:mood_category_list'), follow=True
        )

        self.assertRedirects(response, reverse('dashboard'))
        self.assertContains(response, 'reserved for administrators')

    def test_create_update_and_delete_flow(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse('mood_category:mood_category_create'), {'name': 'Calm'}
        )
        self.assertRedirects(response, reverse('mood_category:mood_category_list'))
        category = MoodCategory.objects.get(name='Calm')

        response = self.client.post(
            reverse('mood_category:mood_category_update', args=[category.pk]), {'name': 'Calm Mind'}
        )
        self.assertRedirects(response, reverse('mood_category:mood_category_list'))
        category.refresh_from_db()
        self.assertEqual(category.name, 'Calm Mind')

        response = self.client.post(
            reverse('mood_category:mood_category_delete', args=[category.pk])
        )
        self.assertRedirects(response, reverse('mood_category:mood_category_list'))
        self.assertFalse(MoodCategory.objects.filter(pk=category.pk).exists())

    def test_edit_page_prefills_category_name(self):
        self.client.force_login(self.staff)

        response = self.client.get(
            reverse('mood_category:mood_category_update', args=[self.category.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="Happy"')
        self.assertContains(response, 'Edit Mood Category')

    def test_duplicate_name_is_rejected_case_insensitively(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse('mood_category:mood_category_create'), {'name': 'hAPPY'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'already exists')
        self.assertEqual(MoodCategory.objects.count(), 1)

    def test_cannot_delete_category_that_has_entries(self):
        MoodEntry.objects.create(category=self.category)
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse('mood_category:mood_category_delete', args=[self.category.pk]),
            follow=True,
        )

        self.assertTrue(MoodCategory.objects.filter(pk=self.category.pk).exists())
        self.assertContains(response, 'Cannot delete a mood category')
