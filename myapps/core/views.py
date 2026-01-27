from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from myapps.accounts.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.db import connection
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from myapps.super_admin.models import GlobalSetting



# Create your views here.
def home(request):
  return redirect('login')

from django.utils import timezone
from datetime import timedelta
from myapps.school_admin.utils import log_action

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser and connection.schema_name == 'public':
            return redirect('super_admin_dashboard')
        if request.user.is_school_admin():
            return redirect('school_admin_dashboard')
        if request.user.is_teacher():
            return redirect('teacher_dashboard')
        if request.user.is_student():
            return redirect('student_dashboard')
        if request.user.is_parent():
            return redirect('parent_dashboard')
    
    if request.method == 'POST':
        # 0. Honeypot check for bots
        if request.POST.get('email_confirm'):
            log_action(None, 'SECURITY', 'User', None, "Bot detected via Honeypot field on login page.", request=request)
            return render(request, 'login_page.html')

        username = request.POST.get('username')
        user_candidate = User.objects.filter(username=username).first()

        # 1. Check Lockout Status
        if user_candidate and user_candidate.lockout_until:
            if timezone.now() < user_candidate.lockout_until:
                diff = user_candidate.lockout_until - timezone.now()
                minutes = int(diff.total_seconds() // 60)
                messages.error(request, f'Account locked due to multiple failed attempts. Try again in {minutes} minutes.')
                log_action(None, 'SECURITY', 'User', user_candidate.custom_id, f"Blocked login attempt for locked account: {username}", request=request)
                return render(request, 'login_page.html')
            else:
                # Lockout expired, reset it but don't reset attempts yet (must login successfully)
                user_candidate.lockout_until = None
                user_candidate.save()

        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()

            if not user.is_active:
                messages.error(request, 'Account is disabled.')
                return redirect('login')
            
            # Reset security fields on success
            user.failed_login_attempts = 0
            user.lockout_until = None
            user.save()

            login(request, user)
            log_action(user, 'SECURITY', 'User', user.custom_id, f"Successful login for {user.username}", request=request)

            if user.is_superuser and connection.schema_name == 'public':
                return redirect('super_admin_dashboard')
            if user.is_school_admin():
                return redirect('school_admin_dashboard')
            if user.is_teacher():
                return redirect('teacher_dashboard')
            if user.is_student():
                return redirect('student_dashboard')
            if user.is_parent():
                return redirect('parent_dashboard')
        else:
            # Handle Failure
            if user_candidate:
                user_candidate.failed_login_attempts += 1
                if user_candidate.failed_login_attempts >= 5:
                    user_candidate.lockout_until = timezone.now() + timedelta(minutes=15)
                    log_action(None, 'SECURITY', 'User', user_candidate.custom_id, f"Account locked for user: {username} after 5 failed attempts.", request=request)
                else:
                    log_action(None, 'SECURITY', 'User', user_candidate.custom_id, f"Failed login attempt ({user_candidate.failed_login_attempts}/5) for user: {username}", request=request)
                user_candidate.save()
            
            messages.error(request, 'Invalid username or password')


    return render(request, 'login_page.html')

def impersonate_receive(request, token):
    signer = TimestampSigner()
    try:
        # Token expires in 60 seconds for security
        value = signer.unsign(token, max_age=60)
        tenant_pk, superuser_pk = value.split(':')
    except (SignatureExpired, BadSignature, ValueError):
        messages.error(request, "Impersonation link expired or invalid.")
        return redirect('login')
    
    # We are in the tenant context already thanks to Middleware
    # Find a school admin to impersonate
    impersonate_target = User.objects.filter(role='school_admin', is_active=True).first()
    
    if not impersonate_target:
        messages.error(request, "No active administrator found in this school to impersonate.")
        return redirect('login')
    
    # Perform the login
    login(request, impersonate_target)
    messages.success(request, f"Support Mode: You are now impersonating {impersonate_target.get_full_name()} (Admin)")
    
    return redirect('school_admin_dashboard')


def logout_view(request):
  logout(request)
  return redirect('login')

def maintenance_view(request):
    # Only redirect if maintenance is actually active (safety check)
    if not GlobalSetting.is_maintenance_active() and not request.user.is_superuser:
        return redirect('login')
    return render(request, 'maintenance.html')


