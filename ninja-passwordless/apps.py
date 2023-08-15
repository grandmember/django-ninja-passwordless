from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class NinjapasswordlessConfig(AppConfig):
    name = 'ninjapasswordless'
    verbose = _("Ninja Passwordless")

    def ready(self):
        import ninjapasswordless.signals
