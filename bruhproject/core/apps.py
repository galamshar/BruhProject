from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'bruhproject.core'

    def ready(self) -> None:
        from .background import run_in_background
        from .background import rabbit_background
        #run_in_background(rabbit_background)
