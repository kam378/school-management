from django.apps import AppConfig
class CustomersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapps.customers'  # CHANGED: Added 'myapps.'