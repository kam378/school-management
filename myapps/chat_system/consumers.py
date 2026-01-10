import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context, get_tenant_domain_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope['user']
        # Tenant is now provided by TenantAwareMiddleware in scope
        self.tenant = self.scope.get('tenant')

        if not self.tenant:
            # Fallback for Public/Localhost access where Middleware might return None
            from django_tenants.utils import get_public_schema_name, get_tenant_model
            TenantModel = get_tenant_model()
            try:
                public_schema = get_public_schema_name()
                self.tenant = await database_sync_to_async(TenantModel.objects.get)(schema_name=public_schema)
                # Also ensure connection is set (middleware might have skipped it)
                from django.db import connection
                connection.set_tenant(self.tenant)
            except TenantModel.DoesNotExist:
                pass

        if not self.tenant or not self.user.is_authenticated:
            print(f"!!! WS REJECT: Tenant={self.tenant}, Auth={self.user.is_authenticated} (User: {self.user})")
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'chat_message')
        
        if message_type == 'chat_message':
            message = text_data_json['message']
            # Save message to DB
            await self.save_message(self.user, self.room_name, message)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': self.user.username
                }
            )
        elif message_type == 'typing':
            # Broadcast typing event
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_typing',
                    'sender': self.user.username,
                    'is_typing': text_data_json.get('is_typing', True)
                }
            )
        elif message_type == 'read_receipt':
            # Mark messages as read in DB
            await self.mark_messages_read(self.user, self.room_name)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_read_receipt',
                    'sender': self.user.username,
                    'room_name': self.room_name
                }
            )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'sender': sender
        }))

    async def chat_typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'sender': event['sender'],
            'is_typing': event['is_typing']
        }))

    async def chat_read_receipt(self, event):
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'sender': event['sender'],
            'room_name': event['room_name']
        }))

    @database_sync_to_async
    def save_message(self, user, room, message):
        from .models import ChatMessage
        with schema_context(self.tenant.schema_name):
            ChatMessage.objects.create(sender=user, room_name=room, content=message)

    @database_sync_to_async
    def mark_messages_read(self, user, room):
        from .models import ChatMessage
        from django.utils import timezone
        from django.db.models import Q
        with schema_context(self.tenant.schema_name):
            # Mark all messages in this room NOT sent by me as read
            ChatMessage.objects.filter(
                room_name=room, 
                is_read=False
            ).exclude(sender=user).update(is_read=True, read_at=timezone.now())
