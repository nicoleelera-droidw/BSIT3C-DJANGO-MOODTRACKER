from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect, render

from .models import MoodCategory


@login_required(login_url='login')
def mood_category_list(request):
    """Render the searchable, paginated list of mood categories."""
    query = request.GET.get('q', '').strip()

    categories = MoodCategory.objects.all().order_by('name')

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
def mood_category_create(request):
    """Render the mood category creation form and handle submissions."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()

        if not name:
            messages.error(request, 'Mood category name is required.')
            return redirect('mood_category:mood_category_create')

        if MoodCategory.objects.filter(name__iexact=name).exists():
            messages.error(request, 'A mood category with that name already exists.')
            return redirect('mood_category:mood_category_create')

        MoodCategory.objects.create(name=name)
        messages.success(request, 'Mood category saved successfully.')
        return redirect('mood_category:mood_category_list')

    return render(request, 'mood_category/create.html', {
        'errors': {},
    })
