from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db.models import Q
from django.contrib import messages
from .models import WhiteboardRoom
from .forms import WhiteboardRoomForm
from .agora import generate_room_token
from agora_token_builder import RtcTokenBuilder
from agora_token_builder.RtcTokenBuilder import Role_Publisher, Role_Subscriber
import time

@login_required
def whiteboard_dashboard(request):
    """
    Main entry point.
    Teachers: Manage their rooms.
    Students: View accessible rooms.
    """
    user_role = str(request.user.role).lower()

    if user_role in ['teacher', 'school_admin']:
        # Manager View: Show rooms created by them
        my_rooms = WhiteboardRoom.objects.filter(teacher=request.user).order_by('-created_at')
        return render(request, 'whiteboard/dashboard.html', {
            'rooms': my_rooms,
            'is_teacher': True,
            'base_template': 'teacher_base.html'
        })
    elif user_role == 'student':
        # Student View: Show rooms they are allowed to see
        # We now look directly at M2M relationships instead of relying on StudentProfile
        
        # 1. Explicitly added students (override)
        q_filter = Q(students=request.user)
        
        # 2. Rooms assigned to Classrooms the student is in
        q_filter |= Q(allowed_classrooms__students=request.user)
        
        # 3. Rooms assigned to Grade Levels that have Classrooms the student is in
        q_filter |= Q(allowed_grade_levels__classrooms__students=request.user)

        # 4. Global Visibility: Rooms with NO restrictions at all
        q_filter |= Q(students__isnull=True, allowed_grade_levels__isnull=True, allowed_classrooms__isnull=True)
            
        rooms = WhiteboardRoom.objects.filter(q_filter).distinct().order_by('-created_at')
        
        # Diagnostic info from related models
        from myapps.school_admin.models import Classroom
        user_classroom = Classroom.objects.filter(students=request.user).first()
        profile = getattr(request.user, 'student_profile', None)
        
        return render(request, 'whiteboard/dashboard.html', {
            'rooms': rooms,
            'is_teacher': False,
            'base_template': 'student_base.html',
            'diagnostic': {
                'has_profile': bool(profile),
                'grade_level': str(user_classroom.level) if user_classroom else "Not Assigned",
                'classroom': str(user_classroom) if user_classroom else "Not Assigned",
            }
        })
    else:
        # Fallback for parents or other roles
        return render(request, 'whiteboard/dashboard.html', {
            'rooms': [],
            'is_teacher': False,
            'base_template': 'student_base.html'
        })

@login_required
def whiteboard_create(request):
    if request.user.role not in ['teacher', 'school_admin']:
        return redirect('whiteboard_dashboard')

    if request.method == 'POST':
        form = WhiteboardRoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.teacher = request.user
            # Generate short code
            import secrets
            room.short_code = secrets.token_urlsafe(6)
            room.save()
            form.save_m2m() # Save Many-to-Many data
            messages.success(request, "Whiteboard Room Created!")
            return redirect('whiteboard_dashboard')
    else:
        form = WhiteboardRoomForm()

    return render(request, 'whiteboard/room_form.html', {'form': form, 'title': 'Create New Class'})

@login_required
def whiteboard_edit(request, room_id):
    room = get_object_or_404(WhiteboardRoom, id=room_id, teacher=request.user)
    
    if request.method == 'POST':
        form = WhiteboardRoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, "Room Updated!")
            return redirect('whiteboard_dashboard')
    else:
        form = WhiteboardRoomForm(instance=room)
    
    return render(request, 'whiteboard/room_form.html', {'form': form, 'title': 'Edit Class'})

@login_required
def whiteboard_delete(request, room_id):
    room = get_object_or_404(WhiteboardRoom, id=room_id, teacher=request.user)
    if request.method == 'POST':
        room.delete()
        messages.success(request, "Room Deleted.")
    return redirect('whiteboard_dashboard')

@login_required
def whiteboard_view(request, short_code):
    # 1. Get Room
    room = get_object_or_404(WhiteboardRoom, short_code=short_code)

    # 2. Check Permissions
    is_teacher = (room.teacher == request.user)
    if not is_teacher:
        allowed = False
        
        # 1. Direct assignment
        if room.students.filter(id=request.user.id).exists():
            allowed = True
        
        # 2. Bulk assignment checks (Direct M2M)
        if not allowed:
            # Check if student is in any of the allowed classrooms
            if room.allowed_classrooms.filter(students=request.user).exists():
                allowed = True
            # Check if student is in any class belonging to the allowed grade levels
            elif room.allowed_grade_levels.filter(classrooms__students=request.user).exists():
                allowed = True
        
        # 3. Global Visibility check: Room has NO assignments at all
        if not allowed:
            has_grade_req = room.allowed_grade_levels.exists()
            has_class_req = room.allowed_classrooms.exists()
            has_student_req = room.students.exists()
            
            if not (has_grade_req or has_class_req or has_student_req):
                allowed = True

        if not allowed:
             return render(request, '403.html', {'message': 'You are not enrolled in this class.'}, status=403)
    
    # 3. Generate Token (Server-side)
    try:
        # Fastboard Token
        token = generate_room_token(str(room.room_uuid), is_teacher=is_teacher)
        
        # RTC Video Token
        rtc_uid = request.user.id
        role = Role_Publisher if is_teacher else Role_Subscriber
        
        # Expire in 24 hours
        privilege_expired_ts = int(time.time()) + (3600 * 24)
        
        rtc_token = RtcTokenBuilder.buildTokenWithUid(
            settings.AGORA_APP_ID,
            settings.AGORA_APP_CERTIFICATE,
            str(room.room_uuid),
            rtc_uid,
            role,
            privilege_expired_ts
        )
        
    except Exception as e:
        return render(request, '500.html', {'message': f'Token Error: {e}'}, status=500)

    # 4. Context for Template
    context = {
        'room': room,
        'room_token': token,
        'rtc_token': rtc_token,
        'rtc_uid': rtc_uid,
        'is_writable': is_teacher,
        'AGORA_APP_ID': settings.AGORA_APP_ID,
        'NETLESS_APP_ID': settings.NETLESS_APP_ID,
    }

    return render(request, 'whiteboard/board.html', context)
