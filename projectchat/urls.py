from django.contrib import admin
from django.urls import path, include, re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import room.routing

websocket_urlpatterns = [
    re_path(r'^', AuthMiddlewareStack(
            URLRouter(
                room.routing.websocket_urlpatterns
            )
        ),
    ),
]

urlpatterns = [
    path('', include('core.urls')),
    path('admin/', admin.site.urls),
    path('rooms/', include('room.urls')),
]
