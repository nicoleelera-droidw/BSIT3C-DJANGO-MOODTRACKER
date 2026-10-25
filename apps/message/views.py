from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render

from apps.scoping import scoped_mood_entries
from .models import Message


@login_required(login_url='login')
def message_list(request):
    """Render the signed-in user's messages attached to their mood entries."""
    mood_entries = scoped_mood_entries(request.user).select_related('category').order_by('-created_at')
    messages_qs = Message.objects.filter(mood_entry__in=mood_entries).order_by('-created_at')

    paginator = Paginator(messages_qs, 10)
    page_number = request.GET.get('page', 1)
    messages_page = paginator.get_page(page_number)

    return render(request, 'message/list.html', {
        'messages': messages_page,
    })
