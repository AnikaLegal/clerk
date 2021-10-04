from django.apps import AppConfig


class ActionstepConfig(AppConfig):
    name = "actionstep"

    def handle(self, *args, **kwargs):
        import actionstep.signals
