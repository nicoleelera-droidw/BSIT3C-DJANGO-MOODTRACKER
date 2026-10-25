from django.contrib import admin

from .models import MoodEntry


@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):
    list_display = ('category', 'rating', 'user', 'created_at', 'updated_at')
    list_filter = ('category',)
    search_fields = ('notes',)
