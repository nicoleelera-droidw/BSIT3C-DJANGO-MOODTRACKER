from django.contrib import admin

from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('mood_entry', 'body', 'created_at', 'updated_at')
    list_filter = ('mood_entry',)
    search_fields = ('body',)
