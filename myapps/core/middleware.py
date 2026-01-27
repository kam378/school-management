from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.shortcuts import render
from myapps.school_admin.utils import log_action
import time

class IPThrottlingMiddleware:
    """
    Simple IP-based throttling for sensitive endpoints (like Login).
    Blocks an IP if it makes too many requests in a short window.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only target the login page for this specific throttling
        if request.path == '/login/' and request.method == 'POST':
            ip = self.get_client_ip(request)
            cache_key = f"throttle_login_{ip}"
            
            # Record of timestamps for this IP
            request_history = cache.get(cache_key, [])
            now = time.time()
            
            # Remove old timestamps (older than 60 seconds)
            request_history = [t for t in request_history if now - t < 60]
            
            # If they already did more than 20 requests in the last minute, block
            if len(request_history) >= 20:
                log_action(None, 'SECURITY', 'IP_THROTTLE', None, f"IP {ip} blocked for excessive login requests.", request=request)
                return HttpResponseForbidden("Too many requests from this IP. Please try again in a few minutes.")
            
            # Add current timestamp and update cache
            request_history.append(now)
            cache.get_or_set(cache_key, request_history, 600) # Keep history for 10 mins if they stop
            cache.set(cache_key, request_history, 600)

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
