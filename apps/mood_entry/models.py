"""Defines the mood entries recorded by the mood tracker."""

from django.conf import settings
from django.db import models

from apps.emotion.models import Emotion
from apps.mood_category.models import MoodCategory


class MoodEntry(models.Model):
    category = models.ForeignKey(
        MoodCategory,
        related_name='entries',
        on_delete=models.CASCADE,
    )
    emotion = models.ForeignKey(
        Emotion,
        related_name='entries',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    rating = models.PositiveSmallIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='mood_entries',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tblmoodentry'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.category} ({self.rating})'
