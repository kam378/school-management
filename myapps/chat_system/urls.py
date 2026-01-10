from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_layout, name='chat_home'), # Default view (no active chat)
    path('start/<int:target_id>/', views.start_chat, name='start_chat'),
    path('room/<str:room_name>/', views.chat_layout, name='chat_layout_room'), # Specific room view
    # Redirect old dashboard/room URLs to home if needed, or simply let them 404/redirect
    path('dashboard/', views.chat_layout, name='chat_dashboard'), # Alias for backward compat
]