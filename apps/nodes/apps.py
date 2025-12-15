from django.apps import AppConfig

class NodesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = 'apps.nodes'

    def ready(self):
        # Importa los signals para que se registren al iniciar la app
        import apps.nodes.signals
