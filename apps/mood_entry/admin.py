from django.contrib import admin

from .models import MoodEntry


@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):
    list_display = ('category', 'emotion', 'rating', 'user', 'created_at', 'updated_at')
    list_filter = ('category', 'emotion')
    search_fields = ('notes',)
