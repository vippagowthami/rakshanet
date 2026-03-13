from django.apps import AppConfig


class RakshaConfig(AppConfig):
    name = 'raksha'
    verbose_name = 'RakshaNet Core'

    def ready(self):
        # import signals to wire up priority computation
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass
