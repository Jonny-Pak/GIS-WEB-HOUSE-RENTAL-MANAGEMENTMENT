from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import render


class FriendlyErrorPagesMiddleware:
    # Return HTML 403/404 pages for non-API requests.
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        restricted_prefixes = ('/admin/', '/custom-admin/')
        allowed_admin_paths = (
            '/admin/login/',
            '/admin/jsi18n/',
            '/custom-admin/login/',
        )
        user = getattr(request, 'user', None)
        is_superuser = bool(user and getattr(user, 'is_superuser', False))

        if request.path.startswith(restricted_prefixes):
            if request.path.startswith(allowed_admin_paths):
                pass
            elif not is_superuser:
                return self._render_403(request)

        try:
            response = self.get_response(request)
        except PermissionDenied:
            return self._render_403(request)
        except Http404:
            return self._render_404(request)

        if self._should_override(request, response, 403):
            return self._render_403(request)

        if self._should_override(request, response, 404):
            return self._render_404(request)

        return response

    def _should_override(self, request, response, status_code):
        if response.status_code != status_code:
            return False

        if request.path.startswith('/api/'):
            return False

        accept = request.headers.get('Accept', '')
        content_type = response.get('Content-Type', '')

        if 'application/json' in accept and 'text/html' not in accept:
            return False

        if 'application/json' in content_type:
            return False

        return True

    def _render_403(self, request):
        return render(request, 'errors/403.html', status=403)

    def _render_404(self, request):
        return render(request, 'errors/404.html', status=404)
