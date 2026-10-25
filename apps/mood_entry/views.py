from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect, render

from apps.mood_category.models import MoodCategory
from apps.scoping import scoped_mood_entries
from .models import MoodEntry

MIN_RATING = 1
MAX_RATING = 10


@login_required(login_url='login')
def mood_entry_list(request):
    """Render the signed-in user's searchable, paginated mood entries."""
    query = request.GET.get('q', '').strip()

    mood_entries = scoped_mood_entries(request.user).select_related('category').order_by('-created_at')

    if query:
        mood_entries = mood_entries.filter(Q(category__name__icontains=query) | Q(notes__icontains=query))

    paginator = Paginator(mood_entries, 10)
    page_number = request.GET.get('page', 1)
    mood_entries_page = paginator.get_page(page_number)
    categories = MoodCategory.objects.all().order_by('name')

    return render(request, 'mood_entry/list.html', {
        'mood_entries': mood_entries_page,
        'categories': categories,
        'query': query,
    })


@login_required(login_url='login')
def mood_entry_create(request):
    """Render the mood entry creation form and handle submissions."""
    categories = MoodCategory.objects.all().order_by('name')

    if request.method == 'POST':
        category_id = request.POST.get('category')
        rating = request.POST.get('rating')
        notes = request.POST.get('notes', '').strip()

        category = MoodCategory.objects.filter(pk=category_id).first()
        if category is None:
            messages.error(request, 'Please choose a valid mood category.')
            return redirect('mood_entry:mood_entry_create')

        rating_value = None
        if rating not in (None, ''):
            try:
                rating_value = int(rating)
            except (TypeError, ValueError):
                messages.error(request, 'Rating must be a whole number.')
                return redirect('mood_entry:mood_entry_create')
            if rating_value < MIN_RATING or rating_value > MAX_RATING:
                messages.error(request, f'Rating must be between {MIN_RATING} and {MAX_RATING}.')
                return redirect('mood_entry:mood_entry_create')

        MoodEntry.objects.create(
            category=category,
            rating=rating_value,
            notes=notes,
            user=request.user,
        )
        messages.success(request, 'Mood entry saved successfully.')
        return redirect('mood_entry:mood_entry_list')

    return render(request, 'mood_entry/create.html', {
        'categories': categories,
        'errors': {},
    })
