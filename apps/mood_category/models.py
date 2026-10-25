"""Defines the mood categories that the mood tracker can use."""

from django.db import models


class MoodCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tblmoodcategory'
        ordering = ['name']

    def __str__(self):
        return self.name
