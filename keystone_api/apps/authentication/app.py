from django.apps import AppConfig

from django.contrib.auth.signals import user_logged_in



class BloxorsConfig(AppConfig):
    name = 'authentication'

    def ready(self):
        user_logged_in.connect()
