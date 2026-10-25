from django.shortcuts import get_object_or_404

from apps.info.models import Info
from apps.mood_entry.models import MoodEntry


def scoped_infos(user):
    return Info.objects.filter(user=user)


def scoped_info(user, pk):
    return get_object_or_404(scoped_infos(user), pk=pk)


def scoped_mood_entries(user):
    return MoodEntry.objects.filter(user=user)


def scoped_mood_entry(user, pk):
    return get_object_or_404(scoped_mood_entries(user), pk=pk)
