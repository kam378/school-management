from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # Dashboard
    path('', views.whiteboard_dashboard, name='whiteboard_dashboard'),
    
    # Management
    path('create/', views.whiteboard_create, name='whiteboard_create'),
    path('edit/<int:room_id>/', views.whiteboard_edit, name='whiteboard_edit'),
    path('delete/<int:room_id>/', views.whiteboard_delete, name='whiteboard_delete'),

    # The Frontend Page
    path('room/<str:short_code>/', views.whiteboard_view, name='whiteboard_page'),
    
    # The API Endpoint (Used by JS to get the token)
    path('api/token/', api_views.get_room_token, name='whiteboard_token'),
]