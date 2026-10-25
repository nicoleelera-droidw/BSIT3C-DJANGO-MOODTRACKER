"""Defines the messages attached to a mood entry."""

from django.db import models


class Message(models.Model):
    mood_entry = models.ForeignKey(
        'mood_entry.MoodEntry',
        related_name='messages',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tblmessage'
        ordering = ['-created_at']

    def __str__(self):
        return self.body
