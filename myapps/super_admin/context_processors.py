from .models import GlobalSetting

def branding(request):
    """
    Makes global branding settings available to all templates.
    """
    settings, created = GlobalSetting.objects.get_or_create(pk=1)
    return {
        'global_settings': settings
    }
