# mysite/asgi.py
import os

import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

django.setup()


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Import modules that depend on Django's application registry
from core.routing import websocket_urlpatterns

# Initialize Django ASGI application after setup
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
    ),
})