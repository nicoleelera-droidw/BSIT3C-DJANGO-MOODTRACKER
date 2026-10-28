from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.mood_category.models import MoodCategory
from apps.mood_entry.models import MoodEntry


class HomeViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='user', password='secret1234')

    def test_home_renders_user_dashboard_for_regular_user(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home_user.html')

    def test_home_renders_admin_dashboard_for_staff(self):
        self.user.is_staff = True
        self.user.save()
        self.client.force_login(self.user)

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertIn('total_entries', response.context)

    def test_home_requires_login(self):
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 302)


class AuthWelcomeTests(TestCase):
    def test_login_page_offers_account_creation(self):
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('register'))
        self.assertContains(response, 'Create an account')

    def test_login_redirects_with_welcome_message(self):
        get_user_model().objects.create_user(
            username='wanda', password='secret1234', first_name='Wanda'
        )

        response = self.client.post(
            reverse('login'),
            {'username': 'wanda', 'password': 'secret1234'},
            follow=True,
        )

        self.assertRedirects(response, reverse('dashboard'))
        self.assertContains(response, 'Welcome back, Wanda!')

    def test_registration_signs_user_in_and_welcomes_them(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'newcomer',
                'first_name': 'Nico',
                'last_name': 'Lera',
                'email': 'nico@example.com',
                'password': 'Tr4ckMyM00d!',
                'confirm_password': 'Tr4ckMyM00d!',
            },
            follow=True,
        )

        self.assertRedirects(response, reverse('dashboard'))
        self.assertContains(response, 'Welcome to Mood Tracker, Nico!')
        user = get_user_model().objects.get(username='newcomer')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)


class DashboardStatsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='user', password='secret1234')
        self.category = MoodCategory.objects.create(name='Happy')
        self.client.force_login(self.user)

    def _create_entry(self, days_ago):
        entry = MoodEntry.objects.create(category=self.category, rating=7, user=self.user)
        MoodEntry.objects.filter(pk=entry.pk).update(
            created_at=timezone.now() - timedelta(days=days_ago)
        )
        return entry

    def test_streak_counts_consecutive_days(self):
        self._create_entry(0)
        self._create_entry(1)
        self._create_entry(3)

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.context['current_streak'], 2)

    def test_streak_ends_yesterday_when_today_is_empty(self):
        self._create_entry(1)
        self._create_entry(2)

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.context['current_streak'], 2)

    def test_top_mood_and_last_seven_days(self):
        self._create_entry(0)
        sad = MoodCategory.objects.create(name='Sad')
        for _ in range(2):
            MoodEntry.objects.create(category=sad, user=self.user)

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.context['top_mood']['label'], 'Sad')
        self.assertEqual(response.context['top_mood']['count'], 2)
        self.assertEqual(response.context['entries_last_7_days'], 3)

    def test_trend_has_one_value_per_day(self):
        self._create_entry(0)
        self._create_entry(0)

        response = self.client.get(reverse('dashboard'))

        self.assertEqual(len(response.context['trend_labels']), 14)
        self.assertEqual(len(response.context['trend_values']), 14)
        self.assertEqual(response.context['trend_values'][-1], 2)
        self.assertEqual(sum(response.context['trend_values']), 2)

    def test_dashboard_offers_quick_mood_shortcuts(self):
        response = self.client.get(reverse('dashboard'))

        quick_moods = response.context['quick_moods']
        self.assertTrue(quick_moods)
        self.assertIn('emoji', quick_moods[0])
        self.assertContains(response, 'How are you feeling?')


class ProfileTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='profile',
            password='secret1234',
            first_name='Pat',
            last_name='User',
            email='pat@example.com',
        )
        self.client.force_login(self.user)

    def test_profile_page_renders_current_details(self):
        response = self.client.get(reverse('profile'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'pat@example.com')

    def test_profile_update_saves_names_and_email(self):
        response = self.client.post(
            reverse('profile'),
            {
                'first_name': 'Patricia',
                'last_name': 'Usuario',
                'email': 'patricia@example.com',
            },
            follow=True,
        )

        self.assertRedirects(response, reverse('profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Patricia')
        self.assertEqual(self.user.last_name, 'Usuario')
        self.assertEqual(self.user.email, 'patricia@example.com')
        self.assertContains(response, 'Profile updated successfully.')

    def test_profile_rejects_email_used_by_another_account(self):
        get_user_model().objects.create_user(
            username='other', password='secret1234', email='taken@example.com'
        )

        response = self.client.post(
            reverse('profile'),
            {
                'first_name': 'Pat',
                'last_name': 'User',
                'email': 'taken@example.com',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Email is already in use.')
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'pat@example.com')

    def test_change_password_keeps_user_signed_in(self):
        response = self.client.post(
            reverse('change_password'),
            {
                'current_password': 'secret1234',
                'new_password': 'N3wPass!234',
                'confirm_password': 'N3wPass!234',
            },
            follow=True,
        )

        self.assertRedirects(response, reverse('profile'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('N3wPass!234'))
        self.assertEqual(self.client.get(reverse('dashboard')).status_code, 200)
        self.assertContains(response, 'Password updated successfully.')

    def test_change_password_rejects_wrong_current_password(self):
        response = self.client.post(
            reverse('change_password'),
            {
                'current_password': 'wrong-password',
                'new_password': 'N3wPass!234',
                'confirm_password': 'N3wPass!234',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'current password is incorrect')
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('secret1234'))

    def test_profile_requires_login(self):
        self.client.logout()

        response = self.client.get(reverse('profile'))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response['Location'])
