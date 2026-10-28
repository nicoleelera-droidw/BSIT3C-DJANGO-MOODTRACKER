from django.contrib import admin

from .models import Emotion


@admin.register(Emotion)
class EmotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'emoji', 'tone', 'created_at', 'updated_at')
    list_filter = ('tone',)
    search_fields = ('name', 'description')
