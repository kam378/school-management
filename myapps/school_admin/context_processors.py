from .models import SchoolSettings

def school_settings(request):
    """
    Returns the singleton SchoolSettings object to the context.
    Allows accessing {{ school_settings.enable_chat }} etc. in templates.
    """
    settings = None
    if request.user.is_authenticated:
        # We only care about settings if logged in, usually.
        # Check if table exists to avoid migration errors during setup, 
        # or just try/except.
        try:
             settings = SchoolSettings.objects.first()
             if not settings:
                 # Auto-create if missing (e.g. fresh tenant) - optional, 
                 # but good for safety. View does this too.
                 settings = SchoolSettings.objects.create()
        except Exception:
            # Table might not exist yet during migrations
            settings = None
            
    return {'school_settings': settings}
