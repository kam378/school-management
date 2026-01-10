from rest_framework import serializers
from .models import WhiteboardRoom

class WhiteboardRoomSerializer(serializers.ModelSerializer):
    teacher_email = serializers.SerializerMethodField()
    writable = serializers.SerializerMethodField()  # compute dynamically

    class Meta: # By default, all model fields are included unless explicitly stated. You’re controlling that in Meta.fields, so fine.
        model = WhiteboardRoom
        fields = ('room_uuid', 'short_code', 'subject', 'created_at', 'teacher_email', 'writable')

    def get_teacher_email(self, obj):
        return obj.teacher.email if obj.teacher else "Deleted Teacher"
    
    # Checks request user safely. Only returns True if the user is the teacher.Returns False for students or anonymous requests.
    def get_writable(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.teacher == request.user
        return False
    
# Naming is crucial: get_<field_name> → otherwise DRF ignores it.
# self → the serializer instance.
# obj → the instance of WhiteboardRoom being serialized.