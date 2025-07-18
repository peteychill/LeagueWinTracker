from django.utils.deprecation import MiddlewareMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

class CSRFExemptMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Exempt all API endpoints from CSRF
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
        return None 