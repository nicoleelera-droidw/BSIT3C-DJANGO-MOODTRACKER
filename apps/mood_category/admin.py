from django.contrib import admin

from .models import MoodCategory


@admin.register(MoodCategory)
class MoodCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
