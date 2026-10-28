from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from apps.access import admin_required
from .models import MoodCategory


def _build_form_data(request, mood_category=None):
    return {
        'name': request.POST.get('name', '' if mood_category is None else mood_category.name).strip(),
    }


def _validate_mood_category_form(form_data, *, mood_category=None):
    errors = {}
    name = form_data['name']

    if not name:
        errors['name'] = 'Mood category name is required.'
    else:
        existing_categories = MoodCategory.objects.filter(name__iexact=name)
        if mood_category is not None:
            existing_categories = existing_categories.exclude(pk=mood_category.pk)
        if existing_categories.exists():
            errors['name'] = 'A mood category with that name already exists.'

    return errors


def _render_mood_category_form(request, form_data, errors, *, mood_category=None):
    is_edit = mood_category is not None
    return render(
        request,
        'mood_category/create.html',
        {
            'errors': errors,
            'form_data': form_data,
            'mood_category': mood_category,
            'page_title': 'Edit Mood Category' if is_edit else 'New Mood Category',
            'submit_label': 'Update Mood Category' if is_edit else 'Save Mood Category',
        },
    )


@login_required(login_url='login')
@admin_required
def mood_category_list(request):
    """Render the searchable, paginated list of mood categories."""
    query = request.GET.get('q', '').strip()

    categories = MoodCategory.objects.annotate(entry_count=Count('entries')).order_by('name')

    if query:
        categories = categories.filter(Q(name__icontains=query))

    paginator = Paginator(categories, 10)
    page_number = request.GET.get('page', 1)
    categories_page = paginator.get_page(page_number)

    return render(request, 'mood_category/list.html', {
        'categories': categories_page,
        'query': query,
    })


@login_required(login_url='login')
@admin_required
@require_http_methods(['GET', 'POST'])
def mood_category_create(request):
    """Render the mood category creation form and handle submissions."""
    if request.method == 'POST':
        form_data = _build_form_data(request)
        errors = _validate_mood_category_form(form_data)
        if errors:
            return _render_mood_category_form(request, form_data, errors)

        MoodCategory.objects.create(name=form_data['name'])
        messages.success(request, 'Mood category saved successfully.')
        return redirect('mood_category:mood_category_list')

    return _render_mood_category_form(request, _build_form_data(request), {})


@login_required(login_url='login')
@admin_required
@require_http_methods(['GET', 'POST'])
def mood_category_update(request, pk):
    mood_category = MoodCategory.objects.filter(pk=pk).first()
    if mood_category is None:
        messages.error(request, 'Mood category not found.')
        return redirect('mood_category:mood_category_list')

    if request.method == 'POST':
        form_data = _build_form_data(request, mood_category)
        errors = _validate_mood_category_form(form_data, mood_category=mood_category)
        if errors:
            return _render_mood_category_form(request, form_data, errors, mood_category=mood_category)

        mood_category.name = form_data['name']
        mood_category.save(update_fields=['name', 'updated_at'])
        messages.success(request, 'Mood category updated successfully.')
        return redirect('mood_category:mood_category_list')

    return _render_mood_category_form(request, _build_form_data(request, mood_category), {}, mood_category=mood_category)


@login_required(login_url='login')
@admin_required
@require_http_methods(['POST'])
def mood_category_delete(request, pk):
    mood_category = MoodCategory.objects.filter(pk=pk).first()
    if mood_category is None:
        messages.error(request, 'Mood category not found.')
        return redirect('mood_category:mood_category_list')

    if mood_category.entries.exists():
        messages.error(request, 'Cannot delete a mood category that is already used by mood entries.')
        return redirect('mood_category:mood_category_list')

    mood_category.delete()
    messages.success(request, 'Mood category deleted successfully.')
    return redirect('mood_category:mood_category_list')
