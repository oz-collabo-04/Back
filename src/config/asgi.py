from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

import os

from channels.routing import ProtocolTypeRouter, URLRouter

from common.middleware.jwt_auth import JWTAuthMiddlewareStack
from config.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.settings")


application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": JWTAuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    }
)
