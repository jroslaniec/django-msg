from django.apps import AppConfig


class MsgConfig(AppConfig):
    name = 'msg'

    def ready(self):
        # Make sure that handlers are registered when django is ready
        from .settings import msg_settings
        msg_settings.import_setting('handlers')
