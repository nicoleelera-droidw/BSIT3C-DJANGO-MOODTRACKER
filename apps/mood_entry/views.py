from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect, render
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_http_methods

from apps.message.services import sync_message_for_entry
from apps.mood_category.models import MoodCategory
from apps.scoping import scoped_mood_entries, scoped_mood_entry
from .models import MoodEntry

MIN_RATING = 1
MAX_RATING = 10


def _build_form_data(request, mood_entry=None):
    return {
        'category': request.POST.get('category', str(mood_entry.category_id) if mood_entry and mood_entry.category_id else ''),
        'rating': request.POST.get('rating', '' if mood_entry is None or mood_entry.rating is None else str(mood_entry.rating)),
        'notes': request.POST.get('notes', '' if mood_entry is None else mood_entry.notes),
    }


def _validate_mood_entry_form(form_data):
    errors = {}
    category = MoodCategory.objects.filter(pk=form_data.get('category')).first()

    if category is None:
        errors['category'] = 'Please choose a valid mood category.'

    rating_value = None
    rating = form_data.get('rating')
    if rating not in (None, ''):
        try:
            rating_value = int(rating)
        except (TypeError, ValueError):
            errors['rating'] = 'Rating must be a whole number.'
        else:
            if rating_value < MIN_RATING or rating_value > MAX_RATING:
                errors['rating'] = f'Rating must be between {MIN_RATING} and {MAX_RATING}.'

    return errors, category, rating_value


def _render_mood_entry_form(request, categories, form_data, errors, *, mood_entry=None):
    is_edit = mood_entry is not None
    return render(
        request,
        'mood_entry/create.html',
        {
            'categories': categories,
            'errors': errors,
            'form_data': form_data,
            'mood_entry': mood_entry,
            'page_title': 'Edit Mood Entry' if is_edit else 'New Mood Entry',
            'submit_label': 'Update Mood Entry' if is_edit else 'Save Mood Entry',
        },
    )


@login_required(login_url='login')
def mood_entry_detail(request, pk):
    """Render one of the signed-in user's mood entries with its support message."""
    mood_entry = scoped_mood_entry(request.user, pk)
    support_message = mood_entry.messages.order_by('id').first()

    return render(request, 'mood_entry/detail.html', {
        'mood_entry': mood_entry,
        'support_message': support_message,
    })


@login_required(login_url='login')
def mood_entry_list(request):
    """Render the signed-in user's searchable, filtered, paginated mood entries."""
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    mood_entries = scoped_mood_entries(request.user).select_related('category').prefetch_related('messages').order_by('-created_at')

    if query:
        mood_entries = mood_entries.filter(Q(category__name__icontains=query) | Q(notes__icontains=query))
    if category_id.isdigit():
        mood_entries = mood_entries.filter(category_id=category_id)

    parsed_from = parse_date(date_from)
    parsed_to = parse_date(date_to)
    if parsed_from:
        mood_entries = mood_entries.filter(created_at__date__gte=parsed_from)
    if parsed_to:
        mood_entries = mood_entries.filter(created_at__date__lte=parsed_to)

    paginator = Paginator(mood_entries, 10)
    page_number = request.GET.get('page', 1)
    mood_entries_page = paginator.get_page(page_number)
    categories = MoodCategory.objects.all().order_by('name')

    pagination_params = request.GET.copy()
    pagination_params.pop('page', None)
    pagination_query = pagination_params.urlencode()
    if pagination_query:
        pagination_query += '&'

    return render(request, 'mood_entry/list.html', {
        'mood_entries': mood_entries_page,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'date_from': date_from,
        'date_to': date_to,
        'has_filters': bool(query or category_id or parsed_from or parsed_to),
        'pagination_query': pagination_query,
    })


@login_required(login_url='login')
@require_http_methods(['GET', 'POST'])
def mood_entry_create(request):
    """Render the mood entry creation form and handle submissions."""
    categories = MoodCategory.objects.all().order_by('name')

    if request.method == 'POST':
        form_data = _build_form_data(request)
        errors, category, rating_value = _validate_mood_entry_form(form_data)
        if errors:
            return _render_mood_entry_form(request, categories, form_data, errors)

        mood_entry = MoodEntry.objects.create(
            category=category,
            rating=rating_value,
            notes=form_data['notes'].strip(),
            user=request.user,
        )
        sync_message_for_entry(mood_entry)
        messages.success(request, 'Mood entry saved successfully.')
        return redirect('mood_entry:mood_entry_detail', pk=mood_entry.pk)

    return _render_mood_entry_form(request, categories, _build_form_data(request), {})


@login_required(login_url='login')
@require_http_methods(['GET', 'POST'])
def mood_entry_update(request, pk):
    mood_entry = scoped_mood_entry(request.user, pk)
    categories = MoodCategory.objects.all().order_by('name')

    if request.method == 'POST':
        form_data = _build_form_data(request, mood_entry)
        errors, category, rating_value = _validate_mood_entry_form(form_data)
        if errors:
            return _render_mood_entry_form(request, categories, form_data, errors, mood_entry=mood_entry)

        mood_entry.category = category
        mood_entry.rating = rating_value
        mood_entry.notes = form_data['notes'].strip()
        mood_entry.save()
        sync_message_for_entry(mood_entry)
        messages.success(request, 'Mood entry updated successfully.')
        return redirect('mood_entry:mood_entry_detail', pk=mood_entry.pk)

    return _render_mood_entry_form(request, categories, _build_form_data(request, mood_entry), {}, mood_entry=mood_entry)


@login_required(login_url='login')
@require_http_methods(['POST'])
def mood_entry_delete(request, pk):
    mood_entry = scoped_mood_entry(request.user, pk)
    mood_entry.delete()
    messages.success(request, 'Mood entry deleted successfully.')
    return redirect('mood_entry:mood_entry_list')
