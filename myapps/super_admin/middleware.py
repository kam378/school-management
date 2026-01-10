from django.shortcuts import redirect
from django.urls import reverse
from .models import GlobalSetting

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if maintenance mode is active
        if GlobalSetting.is_maintenance_active():
            # Always allow authenticated superusers to bypass maintenance mode
            if request.user.is_authenticated and request.user.is_superuser:
                return self.get_response(request)
            
            # Allow access to certain pages even during maintenance
            exempt_urls = [
                reverse('maintenance'),
                reverse('login'),  # Allow login page
                '/static/',
                '/media/',
            ]
            
            # Also allow logout and super admin dashboard/login paths
            try:
                exempt_urls.append(reverse('logout'))
                exempt_urls.append(reverse('super_admin_dashboard'))
            except:
                pass  # These might not be available in all URL configs
            
            # Check if current path is exempt
            path = request.path
            is_exempt = any(path.startswith(url) for url in exempt_urls)
            
            if not is_exempt:
                return redirect('maintenance')

        return self.get_response(request)
