from django.test import TestCase

from apps.mood_category.models import MoodCategory
from apps.mood_entry.models import MoodEntry

from .services import FALLBACK_MESSAGES, KEYWORD_MESSAGES, build_support_message, sync_message_for_entry


class SupportMessageTests(TestCase):
    def test_keyword_in_category_selects_matching_message(self):
        category = MoodCategory.objects.create(name='Sad')
        entry = MoodEntry.objects.create(category=category)

        self.assertIn(build_support_message(entry), KEYWORD_MESSAGES['sad'])

    def test_rating_fallback_used_when_category_has_no_keyword(self):
        category = MoodCategory.objects.create(name='Calm')
        high = MoodEntry.objects.create(category=category, rating=9)
        low = MoodEntry.objects.create(category=category, rating=2)

        self.assertEqual(build_support_message(high), FALLBACK_MESSAGES['positive'])
        self.assertEqual(build_support_message(low), FALLBACK_MESSAGES['supportive'])

    def test_sync_creates_only_one_message_per_entry(self):
        category = MoodCategory.objects.create(name='Happy')
        entry = MoodEntry.objects.create(category=category)

        sync_message_for_entry(entry)
        sync_message_for_entry(entry)

        self.assertEqual(entry.messages.count(), 1)

    def test_sync_updates_body_when_mood_changes(self):
        happy = MoodCategory.objects.create(name='Happy')
        sad = MoodCategory.objects.create(name='Sad')
        entry = MoodEntry.objects.create(category=happy)
        message = sync_message_for_entry(entry)
        original_body = message.body

        entry.category = sad
        entry.save()
        sync_message_for_entry(entry)

        message.refresh_from_db()
        self.assertEqual(message.body, build_support_message(entry))
        self.assertNotEqual(message.body, original_body)
        self.assertEqual(entry.messages.count(), 1)
