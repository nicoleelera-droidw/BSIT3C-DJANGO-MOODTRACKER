from functools import wraps

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.http import JsonResponse
from django.shortcuts import redirect

ADMIN_DENIED_MESSAGE = (
    "That page is reserved for administrators. "
    "We've brought you back to your dashboard."
)
SUPERUSER_DENIED_MESSAGE = (
    "Only site administrators can manage user accounts. "
    "We've brought you back to your dashboard."
)


def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def _require(test_func, denied_message):
    def decorator(view_func=None, *, json_response=False):
        def wrap(func):
            @wraps(func)
            def wrapper(request, *args, **kwargs):
                if not request.user.is_authenticated:
                    return redirect_to_login(request.get_full_path(), login_url='login')
                if not test_func(request.user):
                    if json_response:
                        return JsonResponse({'error': denied_message}, status=403)
                    messages.error(request, denied_message)
                    return redirect('dashboard')
                return func(request, *args, **kwargs)

            return wrapper

        if view_func is not None:
            return wrap(view_func)
        return wrap

    return decorator


admin_required = _require(is_admin, ADMIN_DENIED_MESSAGE)
superuser_required = _require(lambda user: user.is_superuser, SUPERUSER_DENIED_MESSAGE)
