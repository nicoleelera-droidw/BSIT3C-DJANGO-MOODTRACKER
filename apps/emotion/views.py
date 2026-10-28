from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from apps.access import admin_required, is_admin
from .models import Emotion

MAX_EMOJI_LENGTH = 8
PAGE_SIZE = 12


def _build_form_data(request, emotion=None):
    return {
        'name': request.POST.get('name', '' if emotion is None else emotion.name).strip(),
        'emoji': request.POST.get('emoji', '' if emotion is None else emotion.emoji).strip(),
        'tone': request.POST.get(
            'tone', Emotion.Tone.NEUTRAL if emotion is None else emotion.tone
        ),
        'description': request.POST.get(
            'description', '' if emotion is None else emotion.description
        ).strip(),
    }


def _validate_emotion_form(form_data, *, emotion=None):
    errors = {}
    name = form_data['name']

    if not name:
        errors['name'] = 'Emotion name is required.'
    else:
        duplicates = Emotion.objects.filter(name__iexact=name)
        if emotion is not None:
            duplicates = duplicates.exclude(pk=emotion.pk)
        if duplicates.exists():
            errors['name'] = 'An emotion with that name already exists.'

    if len(form_data['emoji']) > MAX_EMOJI_LENGTH:
        errors['emoji'] = 'Use a single emoji (up to 8 characters).'

    if form_data['tone'] not in Emotion.Tone.values:
        errors['tone'] = 'Please choose a valid tone.'

    return errors


def _render_emotion_form(request, form_data, errors, *, emotion=None):
    is_edit = emotion is not None
    return render(
        request,
        'emotion/create.html',
        {
            'errors': errors,
            'form_data': form_data,
            'emotion': emotion,
            'tones': Emotion.Tone.choices,
            'page_title': 'Edit Emotion' if is_edit else 'New Emotion',
            'submit_label': 'Update Emotion' if is_edit else 'Save Emotion',
        },
    )


@login_required(login_url='login')
def emotion_list(request):
    """Render the emotion library, searchable and filterable by tone."""
    query = request.GET.get('q', '').strip()
    tone = request.GET.get('tone', '').strip()

    emotions = Emotion.objects.annotate(entry_count=Count('entries')).order_by('name')

    if query:
        emotions = emotions.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if tone in Emotion.Tone.values:
        emotions = emotions.filter(tone=tone)
    else:
        tone = ''

    paginator = Paginator(emotions, PAGE_SIZE)
    emotions_page = paginator.get_page(request.GET.get('page', 1))

    pagination_params = request.GET.copy()
    pagination_params.pop('page', None)
    pagination_query = pagination_params.urlencode()
    if pagination_query:
        pagination_query += '&'

    return render(request, 'emotion/list.html', {
        'emotions': emotions_page,
        'query': query,
        'tone': tone,
        'tones': Emotion.Tone.choices,
        'has_filters': bool(query or tone),
        'pagination_query': pagination_query,
        'can_manage': is_admin(request.user),
    })


@login_required(login_url='login')
@admin_required
@require_http_methods(['GET', 'POST'])
def emotion_create(request):
    """Render the emotion creation form and handle submissions."""
    if request.method == 'POST':
        form_data = _build_form_data(request)
        errors = _validate_emotion_form(form_data)
        if errors:
            return _render_emotion_form(request, form_data, errors)

        Emotion.objects.create(
            name=form_data['name'],
            emoji=form_data['emoji'],
            tone=form_data['tone'],
            description=form_data['description'],
        )
        messages.success(request, 'Emotion saved successfully.')
        return redirect('emotion:emotion_list')

    return _render_emotion_form(request, _build_form_data(request), {})


@login_required(login_url='login')
@admin_required
@require_http_methods(['GET', 'POST'])
def emotion_update(request, pk):
    emotion = Emotion.objects.filter(pk=pk).first()
    if emotion is None:
        messages.error(request, 'Emotion not found.')
        return redirect('emotion:emotion_list')

    if request.method == 'POST':
        form_data = _build_form_data(request, emotion)
        errors = _validate_emotion_form(form_data, emotion=emotion)
        if errors:
            return _render_emotion_form(request, form_data, errors, emotion=emotion)

        emotion.name = form_data['name']
        emotion.emoji = form_data['emoji']
        emotion.tone = form_data['tone']
        emotion.description = form_data['description']
        emotion.save()
        messages.success(request, 'Emotion updated successfully.')
        return redirect('emotion:emotion_list')

    return _render_emotion_form(
        request, _build_form_data(request, emotion), {}, emotion=emotion
    )


@login_required(login_url='login')
@admin_required
@require_http_methods(['POST'])
def emotion_delete(request, pk):
    emotion = Emotion.objects.filter(pk=pk).first()
    if emotion is None:
        messages.error(request, 'Emotion not found.')
        return redirect('emotion:emotion_list')

    if emotion.entries.exists():
        messages.error(request, 'Cannot delete an emotion that is already used by mood entries.')
        return redirect('emotion:emotion_list')

    emotion.delete()
    messages.success(request, 'Emotion deleted successfully.')
    return redirect('emotion:emotion_list')
