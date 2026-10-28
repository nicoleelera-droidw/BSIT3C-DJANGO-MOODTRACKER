"""Defines the emotions that mood entries can be tagged with."""

from django.db import models


class Emotion(models.Model):
    class Tone(models.TextChoices):
        POSITIVE = 'positive', 'Positive'
        NEUTRAL = 'neutral', 'Neutral'
        NEGATIVE = 'negative', 'Negative'

    TONE_BADGES = {
        Tone.POSITIVE: 'bg-green-lt text-green',
        Tone.NEUTRAL: 'bg-secondary-lt text-secondary',
        Tone.NEGATIVE: 'bg-red-lt text-red',
    }

    name = models.CharField(max_length=80, unique=True)
    emoji = models.CharField(max_length=8, blank=True)
    tone = models.CharField(max_length=10, choices=Tone.choices, default=Tone.NEUTRAL)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tblemotion'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def tone_badge_class(self):
        return self.TONE_BADGES[self.tone]
