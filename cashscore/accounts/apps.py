from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'cashscore.accounts'

    def ready(self):
        from . import signals
