from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from myapps.customers.models import Client, Domain
from .forms import TenantForm, SubscriptionPlanForm, GlobalSettingsForm, SuperAdminUserForm, PlatformResourceForm
from myapps.accounts.models import User
from .models import GlobalSetting, SubscriptionPlan, PlatformAuditLog
from .utils import QuotaManager
from myapps.school_admin.utils import log_action
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.signing import TimestampSigner





def super_admin_check(user):
    return user.is_authenticated and user.is_superuser

from django_tenants.utils import schema_context

@user_passes_test(super_admin_check)
def dashboard(request):
    schools = Client.objects.exclude(schema_name='public')
    total_schools = schools.count()
    
    # Live Cross-Schema Analytics
    total_students = 0
    total_teachers = 0
    total_parents = 0
    
    for school in schools:
        with schema_context(school.schema_name):
            total_students += User.objects.filter(role='student').count()
            total_teachers += User.objects.filter(role='teacher').count()
            total_parents += User.objects.filter(role='parent').count()
    
    recent_schools = schools.order_by('-created_on')[:5]
    for school in recent_schools:
        with schema_context(school.schema_name):
            school.student_count = User.objects.filter(role='student').count()
    
    context = {
        'total_schools': total_schools,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_parents': total_parents,
        'recent_schools': recent_schools,
        'maintenance_active': GlobalSetting.is_maintenance_active(),
    }
    return render(request, 'super_admin_dashboard.html', context)


@user_passes_test(super_admin_check)
def tenant_list(request):
    schools = Client.objects.exclude(schema_name='public')
    
    # Handle search query
    search_query = request.GET.get('search', '').strip()
    if search_query:
        from django.db.models import Q
        schools = schools.filter(
            Q(name__icontains=search_query) |
            Q(schema_name__icontains=search_query)
        )
    
    for school in schools:
        with schema_context(school.schema_name):
            school.student_count = User.objects.filter(role='student').count()
            school.teacher_count = User.objects.filter(role='teacher').count()
            school.parent_count = User.objects.filter(role='parent').count()
            school.quota_stats = QuotaManager.get_usage_stats(school)
            
            # Get admin user info for impersonation
            admin_user = User.objects.filter(role='school_admin', is_active=True).first()
            school.admin_username = admin_user.username if admin_user else "No admin found"
            school.admin_exists = bool(admin_user)
            
    return render(request, 'super_admin_schools.html', {
        'schools': schools,
        'search_query': search_query,
    })




@user_passes_test(super_admin_check)
def tenant_create(request):
    if request.method == 'POST':
        form = TenantForm(request.POST)
        if form.is_valid():
            tenant = form.save()
            domain_name = form.cleaned_data['domain_name']
            Domain.objects.create(
                domain=domain_name,
                tenant=tenant,
                is_primary=True
            )
            
            # Create default school_admin user for the new tenant
            with schema_context(tenant.schema_name):
                admin_username = f"admin_{tenant.schema_name}"
                admin_email = f"admin@{domain_name}"
                default_password = "Admin@123"  # School should change this immediately
                
                admin_user = User.objects.create_user(
                    username=admin_username,
                    email=admin_email,
                    password=default_password,
                    first_name="School",
                    last_name="Administrator",
                    role="school_admin",
                    is_active=True
                )
            
            messages.success(request, f"School '{tenant.name}' created successfully! Admin user: {admin_username} | Password: {default_password}")
            return redirect('super_admin_schools')
    else:
        form = TenantForm()
    
    return render(request, 'super_admin_school_form.html', {'form': form, 'title': 'Create New School'})


@user_passes_test(super_admin_check)
def tenant_edit(request, pk):
    tenant = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = TenantForm(request.POST, instance=tenant)
        if form.is_valid():
            tenant = form.save()
            domain_name = form.cleaned_data['domain_name']
            # Update or create primary domain
            domain, created = Domain.objects.get_or_create(
                tenant=tenant,
                is_primary=True,
                defaults={'domain': domain_name}
            )
            if not created:
                domain.domain = domain_name
                domain.save()
                
            messages.success(request, f"School '{tenant.name}' updated successfully!")
            return redirect('super_admin_schools')
    else:
        form = TenantForm(instance=tenant)
    
    return render(request, 'super_admin_school_form.html', {'form': form, 'tenant': tenant, 'title': 'Edit School'})

@user_passes_test(super_admin_check)
def tenant_delete(request, pk):
    tenant = get_object_or_404(Client, pk=pk)
    if tenant.schema_name == 'public':
        messages.error(request, "Cannot delete public schema.")
    else:
        name = tenant.name
        tenant.delete()
        messages.success(request, f"School '{name}' deleted.")
    return redirect('super_admin_schools')

@user_passes_test(super_admin_check)
def impersonate_tenant(request, pk):
    tenant = get_object_or_404(Client, pk=pk)
    domain = tenant.domains.filter(is_primary=True).first()
    
    if not domain:
        messages.error(request, "This school has no primary domain configured.")
        return redirect('super_admin_schools')
    
    # Generate a secure token
    signer = TimestampSigner()
    # Token includes tenant ID and user ID for cross-verification
    token = signer.sign(f"{tenant.pk}:{request.user.pk}")
    
    # Redirect to tenant domain impersonation receiver
    protocol = 'https' if request.is_secure() else 'http'
    # For local development we might need to handle port 8000
    host = domain.domain
    if 'localhost' in host and ':8000' not in host:
        host = f"{host}:8000"
        
    target_url = f"{protocol}://{host}/impersonate/{token}/"
    return redirect(target_url)

@user_passes_test(super_admin_check)

def toggle_maintenance(request):
    settings, created = GlobalSetting.objects.get_or_create(pk=1)
    settings.maintenance_mode = not settings.maintenance_mode
    settings.save()
    
    if settings.maintenance_mode:
        messages.success(request, "Global Maintenance Mode Activated!")
    else:
        messages.success(request, "Global Maintenance Mode Deactivated!")


    state = "activated" if settings.maintenance_mode else "deactivated"
    messages.success(request, f"Global Maintenance Mode {state}!")
    return redirect('super_admin_dashboard')

@user_passes_test(super_admin_check)
def plan_list(request):
    plans = SubscriptionPlan.objects.all()
    return render(request, 'super_admin_plans.html', {'plans': plans})

@user_passes_test(super_admin_check)
def plan_create(request):
    if request.method == 'POST':
        form = SubscriptionPlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Subscription Plan created.")
            return redirect('super_admin_plans')
    else:
        form = SubscriptionPlanForm()
    return render(request, 'super_admin_plan_form.html', {'form': form, 'title': 'Create Plan'})

@user_passes_test(super_admin_check)
def plan_edit(request, pk):
    plan = get_object_or_404(SubscriptionPlan, pk=pk)
    if request.method == 'POST':
        form = SubscriptionPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, "Subscription Plan updated.")
            return redirect('super_admin_plans')
    else:
        form = SubscriptionPlanForm(instance=plan)
    return render(request, 'super_admin_plan_form.html', {'form': form, 'title': 'Edit Plan'})

@user_passes_test(super_admin_check)
def plan_delete(request, pk):
    plan = get_object_or_404(SubscriptionPlan, pk=pk)
    name = plan.name
    plan.delete()
    messages.success(request, f"Plan '{name}' deleted.")
    return redirect('super_admin_plans')


@user_passes_test(super_admin_check)
def system_settings(request):
    settings, created = GlobalSetting.objects.get_or_create(pk=1)
    if request.method == 'POST':
        form = GlobalSettingsForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Global system settings updated successfully!")
            return redirect('system_settings')
    else:
        form = GlobalSettingsForm(instance=settings)
    
    return render(request, 'super_admin_settings.html', {'form': form, 'settings': settings})

from .models import PlatformResource
from .forms import PlatformResourceForm

@user_passes_test(super_admin_check)
def manage_platform_resources(request):
    resources = PlatformResource.objects.all()
    
    q = request.GET.get('q', '').strip()
    if q:
        resources = resources.filter(Q(title__icontains=q) | Q(description__icontains=q))
        
    resources = resources.order_by('-created_at')
    if request.method == 'POST':
        form = PlatformResourceForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Global platform resource added successfully!")
            return redirect('manage_platform_resources')
    else:
        form = PlatformResourceForm()
    
    return render(request, 'super_admin_resources.html', {
        'resources': resources,
        'form': form
    })

@user_passes_test(super_admin_check)
def delete_platform_resource(request, pk):
    resource = get_object_or_404(PlatformResource, pk=pk)
    title = resource.title
    resource.delete()
    messages.warning(request, f"Global resource '{title}' has been deleted.")
    return redirect('manage_platform_resources')

@user_passes_test(super_admin_check)
def toggle_theme(request):
    settings, created = GlobalSetting.objects.get_or_create(pk=1)
    settings.is_dark_mode = not settings.is_dark_mode
    settings.save()
    messages.success(request, f"Theme switched to {'Dark' if settings.is_dark_mode else 'Light'} mode.")
    return redirect(request.META.get('HTTP_REFERER', 'super_admin_dashboard'))

from .models import PlatformAuditLog
from django.core.paginator import Paginator
from django.db.models import Q

@user_passes_test(super_admin_check)
def platform_audit_logs(request):
    logs_list = PlatformAuditLog.objects.all().order_by('-timestamp')
    
    # Filtering
    action_filter = request.GET.get('action')
    if action_filter:
        logs_list = logs_list.filter(action=action_filter)

    search_query = request.GET.get('search')
    if search_query:
        logs_list = logs_list.filter(
            Q(user__username__icontains=search_query) |
            Q(details__icontains=search_query) |
            Q(target_model__icontains=search_query) |
            Q(target_id__icontains=search_query)
        )

    paginator = Paginator(logs_list, 50) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    from myapps.accounts.models import AUDIT_ACTION_CHOICES
    context = {
        'page_obj': page_obj,
        'action_choices': AUDIT_ACTION_CHOICES,
        'current_action': action_filter,
        'search_query': search_query,
    }

    return render(request, 'super_admin_audit_logs.html', context)

@user_passes_test(super_admin_check)
def super_admin_user_list(request):
    admins = User.objects.filter(is_superuser=True).order_by('username')
    return render(request, 'super_admin_users.html', {'admins': admins})

@user_passes_test(super_admin_check)
def super_admin_user_create(request):
    if request.method == 'POST':
        form = SuperAdminUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            log_action(request.user, 'CREATE', 'User (Super Admin)', user.pk, f"Created super admin account: {user.username}")
            messages.success(request, f"Super Admin '{user.username}' created successfully.")
            return redirect('super_admin_users')
    else:
        form = SuperAdminUserForm()
    return render(request, 'super_admin_user_form.html', {'form': form, 'title': 'Add Administrator'})

@user_passes_test(super_admin_check)
def super_admin_user_edit(request, pk):
    admin = get_object_or_404(User, pk=pk, is_superuser=True)
    if request.method == 'POST':
        form = SuperAdminUserForm(request.POST, instance=admin)
        if form.is_valid():
            form.save()
            log_action(request.user, 'UPDATE', 'User (Super Admin)', admin.pk, f"Updated super admin account: {admin.username}")
            messages.success(request, f"Super Admin '{admin.username}' updated successfully.")
            return redirect('super_admin_users')
    else:
        form = SuperAdminUserForm(instance=admin)
    return render(request, 'super_admin_user_form.html', {'form': form, 'title': f'Edit Admin: {admin.username}'})

@user_passes_test(super_admin_check)
def super_admin_user_delete(request, pk):
    admin = get_object_or_404(User, pk=pk, is_superuser=True)
    if admin == request.user:
        messages.error(request, "Security Breach Prevention: You cannot terminate your own administrative root session.")
    else:
        try:
            username = admin.username
            # We use raw SQL deletion here because standard admin.delete() triggers 
            # a Django Collector check for related objects in ALL installed apps.
            # In a multi-tenant setup, tenant-specific tables (like 'core_notification')
            # do not exist in the public schema, causing a "relation does not exist" error.
            # Raw SQL deletion bypasses the Django collector while still respecting 
            # actual database-level constraints in the public schema.
            from django.db import connection
            with connection.cursor() as cursor:
                # 1. Nullify references in public schema tables that would block deletion
                cursor.execute("UPDATE super_admin_platformauditlog SET user_id = NULL WHERE user_id = %s", [admin.pk])
                cursor.execute("UPDATE django_admin_log SET user_id = NULL WHERE user_id = %s", [admin.pk])
                
                # 2. Finally, delete the user
                cursor.execute("DELETE FROM accounts_user WHERE id = %s", [admin.pk])
                
            log_action(request.user, 'DELETE', 'User (Super Admin)', pk, f"Deleted super admin account: {username}")
            messages.success(request, f"System Administrator account '@{username}' has been successfully purged from the registry.")
        except Exception as e:
            messages.error(request, f"Registry Operation Failed: Could not delete admin account. Error: {str(e)}")
    return redirect('super_admin_users')
