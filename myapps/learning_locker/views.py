from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from django_tenants.utils import schema_context
from .models import LearningResource
from .forms import LearningResourceForm
from myapps.school_admin.models import SchoolSettings, Classroom, GradeLevel, Subject
from myapps.super_admin.models import PlatformResource

def is_staff_or_admin(user):
    return user.is_school_admin() or user.is_teacher() or user.is_superuser

@login_required
@user_passes_test(is_staff_or_admin)
def manage_resources(request):
    """
    Admin/Teacher view to manage learning materials.
    """
    user = request.user
    school_settings = SchoolSettings.objects.first()
    
    # Filtering: Super Admins see all. Teachers see what they uploaded or class-related.
    if user.is_superuser or user.is_school_admin():
        resources = LearningResource.objects.all()
    else:
        resources = LearningResource.objects.filter(
            Q(uploaded_by=user) | Q(school_wide=True) | Q(is_platform_global=True)
        )
        
    # Search logic
    q = request.GET.get('q', '').strip()
    if q:
        resources = resources.filter(Q(title__icontains=q) | Q(description__icontains=q))
    
    resources = resources.distinct().order_by('-created_at')

    if request.method == 'POST':
        form = LearningResourceForm(request.POST, request.FILES, user=user)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.uploaded_by = user
            resource.save()
            form.save_m2m() # Important for ManyToMany fields
            messages.success(request, f"Resource '{resource.title}' uploaded successfully.")
            return redirect('learning_locker:manage_resources')
    else:
        form = LearningResourceForm(user=user)

    return render(request, 'learning_locker/manage_resources.html', {
        'resources': resources,
        'form': form,
        'school_settings': school_settings
    })

@login_required
def student_locker(request):
    """
    Student view to browse and download materials.
    """
    user = request.user
    if not user.is_student():
        messages.error(request, "Only students can access the Learning Locker hub.")
        return redirect('dashboard')

    school_settings = SchoolSettings.objects.first()
    
    # 1. Fetch Platform-Wide (Super Admin) Resources from Public Schema
    with schema_context('public'):
        # We fetch them into a list to prevent schema-leak issues once context is closed
        global_resources = list(PlatformResource.objects.all().order_by('-created_at'))
        for r in global_resources:
            r.is_platform_global = True # Ensure template badge works

    # 2. Fetch Tenant-Specific Resources
    from myapps.student.models import StudentProfile
    profile = StudentProfile.objects.filter(student=user).first()
    classroom = profile.classroom if profile else None
    grade_level = classroom.level if classroom else None

    tenant_resources = LearningResource.objects.filter(
        Q(is_platform_global=True) |
        Q(school_wide=True) |
        Q(target_levels=grade_level) |
        Q(target_classrooms=classroom)
    )
    
    # Search logic
    q = request.GET.get('q', '').strip()
    if q:
        # Search tenant resources
        tenant_resources = tenant_resources.filter(Q(title__icontains=q) | Q(description__icontains=q))
        # Search global resources (filter the existing list)
        global_resources = [r for r in global_resources if q.lower() in r.title.lower() or (r.description and q.lower() in r.description.lower())]

    tenant_resources = tenant_resources.distinct().order_by('-created_at')

    # 3. Combine and Group
    # Note: Global resources from public schema are added to the lists
    books = [r for r in global_resources if r.resource_type == 'book'] + \
            list(tenant_resources.filter(resource_type='book'))
            
    videos = [r for r in global_resources if r.resource_type == 'video'] + \
             list(tenant_resources.filter(resource_type='video'))
             
    materials = [r for r in global_resources if r.resource_type == 'document'] + \
                list(tenant_resources.filter(resource_type__in=['document', 'link']))

    return render(request, 'learning_locker/student_locker.html', {
        'books': books,
        'videos': videos,
        'materials': materials,
        'school_settings': school_settings
    })

@login_required
@user_passes_test(is_staff_or_admin)
def delete_resource(request, pk):
    resource = get_object_or_404(LearningResource, pk=pk)
    
    # Permission check
    if not request.user.is_school_admin() and resource.uploaded_by != request.user:
        messages.error(request, "You don't have permission to delete this resource.")
        return redirect('learning_locker:manage_resources')

    if request.method == 'POST':
        title = resource.title
        resource.delete()
        messages.warning(request, f"Resource '{title}' has been removed.")
        return redirect('learning_locker:manage_resources')
    
    return render(request, 'learning_locker/delete_confirm.html', {'resource': resource})
