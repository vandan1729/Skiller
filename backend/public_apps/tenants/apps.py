from django.apps import AppConfig


class TenantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'public_apps.tenants'
    
    def ready(self):
        import public_apps.tenants.signals
