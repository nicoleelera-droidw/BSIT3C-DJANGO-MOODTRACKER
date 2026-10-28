from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.emotion.models import Emotion
from apps.mood_category.models import MoodCategory
from apps.mood_entry.models import MoodEntry

User = get_user_model()


class EmotionLibraryTests(TestCase):
    def setUp(self):
        Emotion.objects.all().delete()
        self.admin = User.objects.create_user(
            username='admin', password='secret1234', is_staff=True
        )
        self.user = User.objects.create_user(username='user', password='secret1234')
        self.joy = Emotion.objects.create(
            name='Joy', emoji='😊', tone=Emotion.Tone.POSITIVE, description='A lifted feeling.'
        )

    def test_regular_user_can_browse_library_without_management_controls(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('emotion:emotion_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Joy')
        self.assertNotContains(response, 'New Emotion')
        self.assertNotContains(response, reverse('emotion:emotion_update', args=[self.joy.pk]))

    def test_admin_sees_management_controls(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse('emotion:emotion_list'))

        self.assertContains(response, 'New Emotion')
        self.assertContains(response, reverse('emotion:emotion_update', args=[self.joy.pk]))

    def test_regular_user_cannot_manage_emotions(self):
        self.client.force_login(self.user)

        for url in (
            reverse('emotion:emotion_create'),
            reverse('emotion:emotion_update', args=[self.joy.pk]),
        ):
            self.assertRedirects(self.client.get(url), reverse('dashboard'))

        response = self.client.post(
            reverse('emotion:emotion_create'),
            {'name': 'Restless', 'tone': 'neutral'},
        )
        self.assertRedirects(response, reverse('dashboard'))
        self.assertFalse(Emotion.objects.filter(name='Restless').exists())

        response = self.client.post(reverse('emotion:emotion_delete', args=[self.joy.pk]))
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(Emotion.objects.filter(pk=self.joy.pk).exists())

    def test_filter_by_tone_and_search(self):
        Emotion.objects.create(name='Sad', tone=Emotion.Tone.NEGATIVE)
        self.client.force_login(self.user)

        response = self.client.get(reverse('emotion:emotion_list'), {'tone': 'negative'})
        self.assertContains(response, 'Sad')
        self.assertNotContains(response, 'Joy')

        response = self.client.get(reverse('emotion:emotion_list'), {'q': 'jo'})
        self.assertContains(response, 'Joy')
        self.assertNotContains(response, 'Sad')

    def test_invalid_tone_filter_is_ignored(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('emotion:emotion_list'), {'tone': 'mixed'})

        self.assertEqual(response.context['emotions'].paginator.count, 1)


class EmotionAdminTests(TestCase):
    def setUp(self):
        Emotion.objects.all().delete()
        self.admin = User.objects.create_user(
            username='admin', password='secret1234', is_staff=True
        )
        self.client.force_login(self.admin)
        self.joy = Emotion.objects.create(name='Joy', tone=Emotion.Tone.POSITIVE)

    def test_create_emotion(self):
        response = self.client.post(
            reverse('emotion:emotion_create'),
            {
                'name': 'Anxious',
                'emoji': '😰',
                'tone': 'negative',
                'description': 'Uneasy and bracing for something uncertain.',
            },
        )

        self.assertRedirects(response, reverse('emotion:emotion_list'))
        emotion = Emotion.objects.get(name='Anxious')
        self.assertEqual(emotion.emoji, '😰')
        self.assertEqual(emotion.tone, Emotion.Tone.NEGATIVE)

    def test_create_requires_a_name(self):
        response = self.client.post(
            reverse('emotion:emotion_create'), {'name': '  ', 'tone': 'neutral'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Emotion name is required.')

    def test_duplicate_name_is_rejected_case_insensitively(self):
        response = self.client.post(
            reverse('emotion:emotion_create'), {'name': 'joy', 'tone': 'positive'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'An emotion with that name already exists.')
        self.assertEqual(Emotion.objects.filter(name__iexact='joy').count(), 1)

    def test_invalid_tone_is_rejected(self):
        response = self.client.post(
            reverse('emotion:emotion_create'), {'name': 'Restless', 'tone': 'mixed'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please choose a valid tone.')
        self.assertFalse(Emotion.objects.filter(name='Restless').exists())

    def test_update_emotion(self):
        response = self.client.post(
            reverse('emotion:emotion_update', args=[self.joy.pk]),
            {
                'name': 'Delight',
                'emoji': '🥰',
                'tone': 'positive',
                'description': 'Warm and happy.',
            },
        )

        self.assertRedirects(response, reverse('emotion:emotion_list'))
        self.joy.refresh_from_db()
        self.assertEqual(self.joy.name, 'Delight')
        self.assertEqual(self.joy.emoji, '🥰')
        self.assertEqual(self.joy.description, 'Warm and happy.')

    def test_update_keeps_own_name(self):
        response = self.client.post(
            reverse('emotion:emotion_update', args=[self.joy.pk]),
            {'name': 'Joy', 'tone': 'positive'},
        )

        self.assertRedirects(response, reverse('emotion:emotion_list'))

    def test_delete_unused_emotion(self):
        response = self.client.post(reverse('emotion:emotion_delete', args=[self.joy.pk]))

        self.assertRedirects(response, reverse('emotion:emotion_list'))
        self.assertFalse(Emotion.objects.filter(pk=self.joy.pk).exists())

    def test_delete_is_blocked_when_emotion_is_used(self):
        category = MoodCategory.objects.create(name='Happy')
        MoodEntry.objects.create(
            category=category, emotion=self.joy, user=self.admin, notes='good day'
        )

        response = self.client.post(
            reverse('emotion:emotion_delete', args=[self.joy.pk]), follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cannot delete an emotion that is already used')
        self.assertTrue(Emotion.objects.filter(pk=self.joy.pk).exists())
