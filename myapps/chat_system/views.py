from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ChatMessage
from django.contrib.auth import get_user_model
from django.db.models import Q, Max

User = get_user_model()

@login_required
def chat_layout(request, room_name=None):
    """
    Unified chat interface.
    Lists contacts on the left (sidebar) and active chat on the right.
    """
    user = request.user
    
    # 1. Get Contacts based on Role Rules
    # Rule: Students/Parents -> Staff/Teachers only
    if user.role in ['student', 'parent']:
        contacts = User.objects.filter(role__in=['teacher', 'school_admin'])
    # Rule: Teachers/Admins -> Everyone (excluding self)
    else:
        contacts = User.objects.all().exclude(id=user.id)
    
    # Optional: Annotate contacts with last message info for sorting/preview
    # This can be complex with raw Django ORM efficiently, usually handled by 
    # a separate 'Conversation' model or complex subqueries. 
    # For now, let's stick to a simple list, sorted by name or recent login.
    contacts = contacts.order_by('first_name', 'username')

    # 2. Handle Active Chat Room
    active_room = None
    chat_history = []
    other_user = None
    
    if room_name:
        # Security: Ensure user is allowed in this room
        # Expected format: private_{id1}_{id2}
        if room_name.startswith("private_"):
            try:
                parts = room_name.split('_')
                if len(parts) >= 3:
                    id1 = int(parts[1])
                    id2 = int(parts[2])
                    
                    if user.id not in [id1, id2]:
                        messages.error(request, "Unauthorized access.")
                        return redirect('chat_home')
                    
                    other_user_id = id1 if user.id == id2 else id2
                    other_user = User.objects.filter(id=other_user_id).first()
                    
                    if other_user:
                        active_room = room_name
                        # Fetch history
                        chat_history = ChatMessage.objects.filter(
                            room_name=room_name
                        ).select_related('sender').order_by('timestamp')
                        
                        # Mark messages as read (if from other user)
                        ChatMessage.objects.filter(
                            room_name=room_name, 
                            is_read=False
                        ).exclude(sender=user).update(is_read=True)

            except ValueError:
                pass

    from myapps.school_admin.models import SchoolSettings
    settings = SchoolSettings.objects.first()

    return render(request, 'chat_system/chat_layout.html', {
        'contacts': contacts,
        'active_room': active_room,
        'chat_history': chat_history,
        'other_user': other_user,
        'user': user,
        'school_settings': settings,
        'debug_role': user.role
    })

@login_required
def start_chat(request, target_id):
    """
    Redirects to the canonical private room URL within the unified layout.
    """
    current_id = request.user.id
    target_id = int(target_id)
    room_name = f"private_{min(current_id, target_id)}_{max(current_id, target_id)}"
    return redirect('chat_layout_room', room_name=room_name)
