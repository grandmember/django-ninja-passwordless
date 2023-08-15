from ninjapasswordless.settings import api_settings
from django.urls import path
from .apis import router as ninjapasswordless_router
from django.urls import include

app_name = 'ninjapasswordless'

urlpatterns = [
    path(api_settings.PASSWORDLESS_AUTH_PREFIX, include(ninjapasswordless_router.urls)),
]