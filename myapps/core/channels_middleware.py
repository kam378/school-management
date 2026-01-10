
from channels.db import database_sync_to_async
from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from django.db import connection
from django_tenants.utils import schema_context, get_tenant_domain_model

User = get_user_model()

class TenantAwareMiddleware:
    """
    Custom middleware to identify the tenant from the Host header 
    and set the schema context for the duration of the request.
    """
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Extract host from headers
        headers = dict(scope.get('headers', {}))
        host = headers.get(b'host', b'').decode().split(':')[0]
        
        # Resolve tenant
        tenant = await self.get_tenant(host)
        
        if tenant:
            # Attach tenant to scope for later use (like in consumers)
            scope['tenant'] = tenant
            
            # Set schema context
            # Note: We don't use a 'with' block here because we need it to persist 
            # for the inner middleware (like AuthMiddlewareStack)
            from django.db import connection
            connection.set_tenant(tenant)
            
            try:
                return await self.inner(scope, receive, send)
            finally:
                # Cleanup if needed, though usually handled by middleware chain
                pass
        else:
            # Fallback to public or close connection? 
            # For now, just continue without tenant (Auth will likely fail)
            return await self.inner(scope, receive, send)

    @database_sync_to_async
    def get_tenant(self, host):
        Domain = get_tenant_domain_model()
        try:
            domain = Domain.objects.select_related('tenant').get(domain=host)
            return domain.tenant
        except Domain.DoesNotExist:
            return None


class TenantAuthMiddleware:
    """
    Custom authentication middleware that works AFTER tenant context is set.
    This ensures session lookups happen in the correct tenant schema.
    """
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Get tenant from scope (set by TenantAwareMiddleware)
        tenant = scope.get('tenant')
        
        if not tenant:
            scope['user'] = AnonymousUser()
            return await self.inner(scope, receive, send)
        
        # Authenticate user within tenant context
        scope['user'] = await self.get_user(scope, tenant)
        
        return await self.inner(scope, receive, send)
    
    @database_sync_to_async
    def get_user(self, scope, tenant):
        """
        Retrieve the user from the session, ensuring we're in the correct tenant schema.
        """
        from django.contrib.sessions.models import Session
        from django.utils import timezone
        
        # Extract session key from cookies
        headers = dict(scope.get('headers', {}))
        cookie_header = headers.get(b'cookie', b'').decode()
        
        # Parse cookies
        cookies = {}
        if cookie_header:
            for cookie in cookie_header.split('; '):
                if '=' in cookie:
                    key, value = cookie.split('=', 1)
                    cookies[key] = value
        
        session_key = cookies.get('sessionid', '')
        
        if not session_key:
            return AnonymousUser()
        
        try:
            # Query session in the TENANT schema
            with schema_context(tenant.schema_name):
                session = Session.objects.get(
                    session_key=session_key,
                    expire_date__gt=timezone.now()
                )
                session_data = session.get_decoded()
                user_id = session_data.get('_auth_user_id')
                
                if user_id:
                    user = User.objects.get(pk=user_id)
                    return user
        except (Session.DoesNotExist, User.DoesNotExist):
            pass
        
        return AnonymousUser()
