# whiteboard/api_views.py
import secrets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import WhiteboardRoom
from .serializers import WhiteboardRoomSerializer
from .agora import generate_room_token


@api_view(['POST']) 
@permission_classes([IsAuthenticated]) 
def get_room_token(request):
    """
    Return a valid Agora token for a given room short_code.
    
    Teacher = writable/admin
    Enrolled students = readonly
    Others = forbidden
    """
    short_code = request.data.get("short_code")
    if not short_code:
        return Response({"error": "short_code is required"}, status=status.HTTP_400_BAD_REQUEST)

    # -------------------------------
    # Fetch room
    # -------------------------------
    try:
        room = WhiteboardRoom.objects.get(short_code=short_code)
    except WhiteboardRoom.DoesNotExist:
        return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)

    # -------------------------------
    # Determine role & membership
    # -------------------------------
    is_teacher = room.teacher == request.user

    if not is_teacher:
        # Student membership check
        if request.user not in room.students.all():
            return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)

    # -------------------------------
    # Generate Agora token
    # -------------------------------
    try:
        token = generate_room_token(room_uuid=str(room.room_uuid), is_teacher=is_teacher)
    except Exception as e:
        return Response({"error": f"Failed to generate token: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # -------------------------------
    # Serialize response
    # -------------------------------
    serializer = WhiteboardRoomSerializer(room, context={'request': request})
    data = serializer.data
    data['token'] = token  # include Agora token
    # writable is handled by serializer → no need to overwrite
    return Response(data)
